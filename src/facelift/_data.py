# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Helpers for fetching the pre-trained models this project is built around.

Due to the size of the models that we are building this project around, we need to fetch
the models outside of the standard PyPi installation.
The following methods handle building an asset manifest that should be released with
each GitHub release.
This asset manifest will then further inform the little downloading script we have
provided where to find and place the assets in the installed package.

This helper utility currently expects the following of the GitHub release:

1. A ``data-manifest.json`` is provided as a GitHub release asset.
2. All models within the asset manifest are included as GitHub release assets.

.. important::
    The ``data-manifest.json`` must following the following structure:

    .. code-block:: json

        {
            "relative filepath from package root for asset": [
                "download url of asset",
                "md5 hash of asset"
            ]
        }

    As an example:

    .. code-block:: json

        {
            "data/encoders/dlib_face_recognition_resnet_model_v1.dat": [
                "https://github.com/stephen-bunn/facelift/releases/download/v0.1.0/dlib_face_recognition_resnet_model_v1.dat",
                "2316b25ae80acf4ad9b620b00071c423"
            ]
        }

Examples:
    >>> from facelift._data import download_data
    >>> download_data(display_progress=True)
    https://... [123 / 456] 26.97%
    Downloaded https://... to ./... (1234567890)
"""

import json
import sys
from hashlib import md5
from io import BytesIO
from pathlib import Path
from typing import Dict, Generator, List, Optional, Tuple

import urllib3

BASE_PATH = Path(__file__).absolute().parent
REPOSITORY_NAME = "stephen-bunn/facelift"
MANIFEST_NAME = "data-manifest.json"
LATEST_RELEASE_URL = f"https://api.github.com/repos/{REPOSITORY_NAME}/releases/latest"
DOWNLOAD_URL_TEMPLATE = (
    f"https://github.com/{REPOSITORY_NAME}/releases/download/"
    "{release_tag}/{asset_name}"
)
DOWNLOAD_CHUNK_SIZE = 2 ** 12


def _download(
    url: str,
    display_progress: bool = False,
    chunk_size: int = DOWNLOAD_CHUNK_SIZE,
) -> Generator[bytes, None, None]:
    """Download the content of a URL iteratively.

    Args:
        url (str):
            The URL to download content from.
        display_progress (bool, optional):
            Flag that will print basic progress updates of the download.
            Defaults to False.
        chunk_size (int, optional):
            The size of chunks to read in the content.
            Defaults to DOWNLOAD_CHUNK_SIZE.

    Raises:
        ValueError:
            When we fail to fetch the given URL.

    Yields:
        Generator[bytes, None, None]:
            A generator of bytes that are less than or equal to the defined chunk size.
    """

    http = urllib3.PoolManager()
    response = http.request(
        "GET", url, preload_content=False, headers={"User-Agent": "urllib3"}
    )
    if response.status not in (200,):
        raise ValueError(f"Failed to fetch data from {url!r}, {response.data!r}")

    total_size = response.getheaders().get("content-length")
    if display_progress and total_size is None:
        print(
            f"Failed to determine Content-Length for {url!r}, "
            "download progress will not be reported"
        )

    current_size = 0
    for chunk in response.stream(chunk_size):
        current_size += len(chunk)
        if display_progress:
            if total_size is None:
                sys.stdout.write(f"\r{url!s} [{current_size} / ?]")
            else:
                sys.stdout.write(
                    f"\r{url!s} [{current_size} / {total_size}] "
                    f"{(total_size / current_size) * 100.0:.2f}%",
                )

        yield chunk

    if display_progress:
        sys.stdout.write("\n")

    response.release_conn()


def _get_latest_release_tag() -> Optional[str]:
    """Get the latest release's tag from GitHub.

    Returns:
        str: The latest release tag.
    """

    release_data = BytesIO()
    for chunk in _download(LATEST_RELEASE_URL):
        release_data.write(chunk)

    release_data.seek(0)
    release_content = json.loads(release_data.read())
    return release_content.get("tag_name")


def _build_manifest_url(release_tag: Optional[str] = None) -> str:
    """Build a release's manifest download URL.

    Args:
        release_tag (Optional[str], optional):
            The release tag of the manifest to fetch.
            Defaults to None which will fetch the latest release.

    Returns:
        str: The release asset manifest URL.
    """

    if release_tag is None:
        release_tag = _get_latest_release_tag()

    return DOWNLOAD_URL_TEMPLATE.format(
        release_tag=release_tag, asset_name=MANIFEST_NAME
    )


def build_manifest(
    release_tag: str, *asset_filepaths: Path
) -> Dict[str, Tuple[str, str]]:
    """Build the manifest content for a proposed release and defined assets.

    Args:
        release_tag (str):
            The release tag the manifest is being built for.
        asset_filepaths (:class:`pathlib.Path`):
            Multiple existing local asset filepaths.

    Raises:
        FileNotFoundError:
            When a given asset filepath does not exist.
        ValueError:
            When a checksum cannot be calculated for one of the given filepaths.

    Returns:
        Dict[str, Tuple[str, str]]: The manifest JSON-serializable dictionary
    """

    manifest = {}
    for filepath in asset_filepaths:
        if not filepath.is_file():
            raise FileNotFoundError(f"No such file {filepath!s} exists")

        relative_path = filepath.relative_to(BASE_PATH)
        checksum = None
        with filepath.open("rb") as file_handle:
            checksum = md5(file_handle.read()).hexdigest()

        if checksum is None:
            raise ValueError(f"Failed to calculate checksum for {filepath!s}")

        manifest[relative_path.as_posix()] = (
            DOWNLOAD_URL_TEMPLATE.format(
                release_tag=release_tag, asset_name=relative_path.name
            ),
            checksum,
        )

    return manifest


def get_remote_manifest(
    release_tag: Optional[str] = None,
) -> Dict[str, Tuple[str, str]]:
    """Get the manifest content from a GitHub release.

    Args:
        release_tag (Optional[str], optional):
            The release tag of the manifest to fetch.
            Defaults to None which fetches the latest release manifest.

    Returns:
        Dict[str, Tuple[str, str]]: The manifest JSON-serializable dictionary
    """

    manifest_data = BytesIO()
    for chunk in _download(_build_manifest_url(release_tag=release_tag)):
        manifest_data.write(chunk)

    manifest_data.seek(0)
    return json.loads(manifest_data.read())


def download_data(
    display_progress: bool = False,
    release_tag: Optional[str] = None,
    chunk_size: int = DOWNLOAD_CHUNK_SIZE,
    validate: bool = True,
):
    """Download the data from a fetched remote release manifest.

    Args:
        display_progress (bool, optional):
            Flag that indicates if you want to display the download progress for assets.
            Defaults to False.
        release_tag (Optional[str], optional):
            The release tag of the assets you want to download.
            Defaults to None which will fetch the latest release assets.
        chunk_size (int, optional):
            The chunk size to use when downloading assets.
            Defaults to DOWNLOAD_CHUNK_SIZE.
        validate (bool, optional):
            If ``False``, will skip checksum validation for all downloaded assets.
            Defaults to True.

    Raises:
        FileExistsError:
            If a file already exists at one of the assets relative file locations.
        ValueError:
            If the downloaded assets fails checksum validation.
    """

    manifest = get_remote_manifest(release_tag=release_tag)
    for relative_path, (asset_url, asset_checksum) in manifest.items():
        asset_path = BASE_PATH.joinpath(relative_path)
        if asset_path.is_file():
            raise FileExistsError(f"File at {asset_path!s} already exists")

        if not asset_path.parent.is_dir():
            asset_path.parent.mkdir(parents=True)

        checksum_hash = md5()
        with asset_path.open("wb") as file_handle:
            for chunk in _download(
                asset_url, display_progress=display_progress, chunk_size=chunk_size
            ):
                file_handle.write(chunk)
                checksum_hash.update(chunk)

        checksum = checksum_hash.hexdigest()
        sys.stdout.write(f"Downloaded {asset_url} to {asset_path} ({checksum})\n")

        if validate and checksum != asset_checksum:
            raise ValueError(
                f"Downloaded asset at {asset_path!s} has invalid checksum "
                f"(got {checksum!s}, expected {asset_checksum!s})"
            )
