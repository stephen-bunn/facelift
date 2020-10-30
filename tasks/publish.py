# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains Invoke task functions for package publishing."""

import json
import os
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import invoke
from github import Github, GithubException

from .utils import report


@lru_cache()
def _get_access_token():
    access_token = os.environ.get("GITHUB_ACCESS_TOKEN")
    if not access_token:
        while access_token is None or len(access_token) <= 0:
            access_token = input("GitHub Access Token: ").strip()

    return access_token


def _get_dist_dirpath(ctx):
    dirpath = Path(ctx.directory).joinpath("dist")
    if not dirpath.is_dir():
        dirpath.mkdir(parents=True)

    return dirpath


def _get_github(ctx):
    return Github(_get_access_token())


def _get_repo(ctx):
    return _get_github(ctx).get_user().get_repo(ctx.package.name)


def _prompt_continue(message):
    prompt = None
    while not prompt or len(prompt) <= 0:
        prompt = input(f"{message}, Continue? [y/n]: ").trim()

    return prompt.startswith("y")


def _verify_release_new(ctx, release_tag):
    try:
        if _get_repo(ctx).get_release(release_tag):
            message = f"release {release_tag} already exists on GitHub"
            report.error(ctx, "publish.github", message)
            raise ValueError(message)
    except GithubException:
        report.debug(
            ctx,
            "publish.github",
            f"release {release_tag} does not already exist on GitHub",
        )


def _verify_commit_exists(ctx, commit_sha):
    try:
        if _get_repo(ctx).get_commit(commit_sha):
            report.debug(
                ctx,
                "publish.github",
                f"found local commit to be tagged ({commit_sha}) on GitHub",
            )
    except GithubException:
        message = f"commit to be tagged ({commit_sha}) is not present on GitHub"
        report.error(ctx, "publish.github", message)
        raise ValueError(message)


def _create_manifest(ctx, release_tag):
    from facelift._data import BASE_PATH, MANIFEST_NAME, build_manifest

    report.debug(ctx, "publish.github", "building asset manifest")
    data_filepaths = [
        asset for asset in BASE_PATH.joinpath("data").glob("**/*") if asset.is_file()
    ]
    manifest = build_manifest(release_tag, *data_filepaths)
    manifest_filepath = _get_dist_dirpath(ctx).joinpath(MANIFEST_NAME)

    report.debug(
        ctx,
        "publish.github",
        f"writing asset manifest to {manifest_filepath}",
    )
    with manifest_filepath.open("w") as file_handle:
        json.dump(manifest, file_handle)

    return manifest, manifest_filepath


def _create_tag(ctx, release_tag, release_name, commit_sha, draft=False):
    report.info(
        ctx,
        "publish.github",
        f"creating release tag {release_tag} on commit {commit_sha}",
    )

    if not draft:
        return _get_repo(ctx).create_git_tag(
            tag=release_tag,
            tag_message=release_name,
            object=commit_sha,
            type="commit",
        )


def _create_release(ctx, release_tag, release_name, release_message, draft=False):
    report.info(
        ctx,
        "publish.github",
        f"creating release {release_name!r} on tag {release_tag}",
    )

    if not draft:
        return _get_repo(ctx).create_git_release(
            tag=release_tag,
            name=release_name,
            message=release_message,
        )


def _get_release_assets(ctx, manifest):
    dist_dirpath = _get_dist_dirpath(ctx)
    dist_assets = [asset for asset in dist_dirpath.iterdir() if asset.is_file()]
    manifest_assets = [
        dist_dirpath.joinpath(relative_path) for relative_path in manifest.keys()
    ]

    return dist_assets + manifest_assets


def _upload_release_assets(ctx, release, asset_filepaths, draft=False):
    uploaded_assets = []

    for filepath in asset_filepaths:
        report.info(ctx, "publish.github", f"uploading asset {filepath}")
        if not draft:
            uploaded_assets.append(release.upload_asset(filepath.as_posix()))

    return uploaded_assets


@invoke.task()
def github(ctx, yes=False, draft=False):
    """Publish the latest pushed commit as a release to GitHub."""

    release_tag = f"v{ctx.version!s}"
    release_name = f"Release {release_tag!s}"
    _verify_release_new(ctx, release_tag)

    local_commit_sha = (
        subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True)
        .stdout.decode("utf-8")
        .strip()
    )
    _verify_commit_exists(ctx, local_commit_sha)

    manifest, manifest_filepath = _create_manifest(ctx, release_tag)

    if not draft and not yes:
        if not _prompt_continue("About to create a GitHub tag"):
            sys.exit(1)

    _create_tag(ctx, release_tag, release_name, local_commit_sha, draft=draft)

    if not draft and not yes:
        if not _prompt_continue("About to create a GitHub release"):
            sys.exit(1)

    release = _create_release(ctx, release_tag, release_name, "", draft=draft)

    release_assets = _get_release_assets(ctx, manifest)
    _upload_release_assets(ctx, release, release_assets, draft=draft)

    if not draft:
        report.success(
            ctx,
            "publish.github",
            f"published release {release_tag} to GitHub <{release.html_url}>",
        )

    report.debug(
        ctx,
        "publish.github",
        f"removing asset manifest at {manifest_filepath} before PyPi publish",
    )
    os.remove(manifest_filepath.as_posix())


@invoke.task()
def pypi(ctx, yes=False, draft=False):
    """Publish existing distributables to PyPi."""

    report.info(ctx, "publish.pypi", "uploading dist to PyPi")

    if not draft and not yes:
        if not _prompt_continue("About to publish to PyPi"):
            sys.exit(1)

    if not draft:
        ctx.run("poetry publish")
        report.success(ctx, "publish.pypi", "published to PyPi")
