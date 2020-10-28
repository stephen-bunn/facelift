# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

"""Contains base Invoke task functions and groups."""

import json
import os
import pathlib
import webbrowser
from getpass import getpass
from tempfile import NamedTemporaryFile

import invoke
import toml

from . import docs, linter, package, publish
from .utils import report

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
CONFIG_FILEPATH = BASE_DIR / "pyproject.toml"

try:
    with CONFIG_FILEPATH.open("r") as config_fg:
        report.debug(
            {}, "tasks", f"loading poetry config from {CONFIG_FILEPATH.as_posix()!s}"
        )
        metadata = toml.load(config_fg)["tool"]["poetry"]
except KeyError as exc:
    raise KeyError(
        "cannot run tasks if pyproject.toml is missing [tool.poetry] section"
    ) from exc


@invoke.task()
def profile(ctx, filename, calltree=False):
    """Run and profile a given Python script."""

    filepath = pathlib.Path(filename)
    if not filepath.is_file():
        report.error(ctx, "profile", f"no such script {filepath!s}")
    else:
        report.debug(
            ctx,
            "profile",
            "this task assumes that you have installed the 'profile' extra dependency",
        )
        if calltree:
            report.info(ctx, "profile", f"profiling script {filepath!s} calltree")
            ctx.run(
                (
                    f"python -m cProfile -o .profile.cprof {filepath!s}"
                    " && pyprof2calltree -k -i .profile.cprof"
                    " && rm -rf .profile.cprof"
                )
            )
        else:
            report.info(ctx, "profile", f"profiling script {filepath!s}")
            report_result = ctx.run(f"pyinstrument -r html {filepath!s}", hide="out")
            with NamedTemporaryFile("w", delete=False, suffix=".html") as file_handle:
                file_handle.write(report_result.stdout)
                webbrowser.open(f"file://{file_handle.name!s}")


@invoke.task(post=[package.test])
def test(ctx):
    """Test the project."""

    report.success(ctx, "test", "testing project")


@invoke.task(post=[docs.build, package.build, package.check])
def build(ctx):
    """Build the project."""

    report.success(ctx, "build", "building project")


@invoke.task(post=[package.clean, docs.clean])
def clean(ctx):
    """Clean the project."""

    report.success(ctx, "clean", "cleaning project")


@invoke.task(post=[linter.black, linter.isort, linter.flake8, linter.mypy])
def lint(ctx):
    """Lint the project."""

    report.success(ctx, "lint", "linting project")


@invoke.task(pre=[clean, lint, test, build])
def release(ctx, draft=False):
    """Publish a release on GitHub and PyPi for the project."""

    if draft:
        report.error(ctx, "publish", "running in draft mode, nothing will be published")

    publish.github(ctx, draft=draft)
    publish.pypi(ctx, draft=draft)


namespace = invoke.Collection(
    build,
    clean,
    test,
    lint,
    docs,
    package,
    profile,
    linter,
    publish,
    release,
)
namespace.configure(
    {
        "metadata": metadata,
        "version": metadata["version"],
        "directory": BASE_DIR,
        "package": {
            "name": metadata["packages"][0]["include"],
            "directory": BASE_DIR / "src" / metadata["packages"][0]["include"],
        },
        "docs": {"directory": BASE_DIR / "docs"},
    }
)
