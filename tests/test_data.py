# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains tests related to the _data module."""

import json
import shutil
import string
from hashlib import md5
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import Dict, Generator, List, Optional
from unittest.mock import ANY, call, patch

import pytest
from hypothesis import given
from hypothesis.strategies import (
    binary,
    dictionaries,
    integers,
    lists,
    none,
    one_of,
    text,
)

from facelift import _data

from .strategies import image_path, pathlib_path


@given(text(string.ascii_letters + string.digits))
def test_download_raises_ValueError_when_status_non_200(url: str):
    with patch("facelift._data.urllib3") as mocked_urllib3:
        mocked_urllib3.PoolManager.return_value.request.return_value.status = 400

        with pytest.raises(ValueError):
            next(_data._download(url))


@given(
    text(string.ascii_letters + string.digits),
    lists(binary(min_size=1), min_size=1, unique=True),
    integers(min_value=1),
)
def test_download(url: str, data: List[bytes], chunk_size: int):
    with patch("facelift._data.urllib3") as mocked_urllib3:
        mocked_http = mocked_urllib3.PoolManager.return_value
        mocked_response = mocked_http.request.return_value
        mocked_response.status = 200
        mocked_response.stream.return_value = iter(data)

        content = list(_data._download(url, chunk_size=chunk_size))
        mocked_http.request.assert_called_once_with(
            "GET",
            url,
            preload_content=False,
            headers=ANY,
        )
        mocked_response.stream.assert_has_calls([call(chunk_size)])
        mocked_http.request.return_value.release_conn.assert_called_once()

        assert content == data


@given(text(string.ascii_letters + string.digits))
def test_get_latest_release_tag(release_tag: Optional[str]):
    with patch("facelift._data._download") as mocked_download:
        mocked_download.return_value = iter(
            [bytes(f'{{"tag_name": "{release_tag}"}}', "utf-8")]
        )

        release_tag = _data._get_latest_release_tag()
        mocked_download.assert_called_once_with(_data.LATEST_RELEASE_URL)
        assert release_tag == release_tag


@given(one_of(text(string.printable), none()))
def test_build_manifest_url(release_tag: Optional[str]):
    with patch(
        "facelift._data._get_latest_release_tag"
    ) as mocked_get_latest_release_tag:
        mocked_get_latest_release_tag.return_value = "test"

        if release_tag is None:
            assert _data._build_manifest_url() == _data.DOWNLOAD_URL_TEMPLATE.format(
                release_tag="test", asset_name=_data.MANIFEST_NAME
            )
        else:
            assert _data._build_manifest_url(
                release_tag
            ) == _data.DOWNLOAD_URL_TEMPLATE.format(
                release_tag=release_tag, asset_name=_data.MANIFEST_NAME
            )


@given(text(string.printable), pathlib_path())
def test_build_manifest_raises_FileNotFoundError_with_missing_filepath(
    releases_tag: str, filepath: Path
):
    with pytest.raises(FileNotFoundError):
        _data.build_manifest(releases_tag, *[filepath])


@given(text(string.printable))
def test_build_manifest_raises_ValueError_when_checksum_fails(release_tag: str):
    filepaths = list(path for path in _data.BASE_PATH.iterdir() if path.is_file())
    with patch("facelift._data.md5") as mocked_md5:
        mocked_md5.return_value.hexdigest.return_value = None

        with pytest.raises(ValueError):
            _data.build_manifest(release_tag, *filepaths)


@given(text(string.ascii_letters + string.digits))
def test_build_manifest(release_tag: str):
    filepaths = list(path for path in _data.BASE_PATH.iterdir() if path.is_file())
    manifest = _data.build_manifest(release_tag, *filepaths)

    assert isinstance(manifest, dict)
    assert len(manifest) == len(filepaths)
    for relative_path, (download_url, checksum) in manifest.items():
        assert isinstance(relative_path, str)
        asset_filepath = _data.BASE_PATH.joinpath(relative_path)
        assert asset_filepath.is_file()

        with asset_filepath.open("rb") as file_handle:
            assert md5(file_handle.read()).hexdigest() == checksum

        assert isinstance(download_url, str)


@given(
    dictionaries(
        text(string.ascii_letters + string.digits),
        text(string.ascii_letters + string.digits),
    ),
    one_of(text(string.printable), none()),
)
def test_get_remote_manifest(manifest_data: Dict[str, str], release_tag: Optional[str]):
    with patch("facelift._data._download") as mocked_download, patch(
        "facelift._data._build_manifest_url"
    ) as mocked_build_manifest_url:
        mocked_download.return_value = iter([bytes(json.dumps(manifest_data), "utf-8")])

        remote_manifest = _data.get_remote_manifest(release_tag=release_tag)
        mocked_build_manifest_url.assert_called_once_with(release_tag=release_tag)

        assert remote_manifest == manifest_data


@given(text(string.printable))
def test_download_data_raises_FileExistsError_if_file_location_already_exists(
    release_tag: str,
):
    with patch("facelift._data.get_remote_manifest") as mocked_get_remote_manifest:
        mocked_get_remote_manifest.return_value = _data.build_manifest(
            release_tag, *[next(_data.BASE_PATH.iterdir())]
        )

        with pytest.raises(FileExistsError):
            _data.download_data()


@given(text(string.printable), lists(binary(min_size=1), min_size=1))
def test_download_data_raise_ValueError_if_checksum_mismatch(
    release_tag: str, data: List[bytes]
):
    manifest = _data.build_manifest(release_tag, *[next(_data.BASE_PATH.iterdir())])
    with TemporaryDirectory(prefix="facelift-test") as temp_dir:
        temp_dirpath = Path(temp_dir)

        with patch(
            "facelift._data.get_remote_manifest"
        ) as mocked_get_remote_manifest, patch(
            "facelift._data._download"
        ) as mocked_download, patch(
            "facelift._data.md5"
        ) as mocked_md5, patch(
            "facelift._data.BASE_PATH", temp_dirpath
        ):
            mocked_get_remote_manifest.return_value = manifest
            mocked_download.return_value = iter(data)
            mocked_md5.return_value.hexdigest.return_value = "not-an-md5-checksum"

            with pytest.raises(ValueError):
                _data.download_data(validate=True)


@given(text(string.printable))
def test_download_data(release_tag: str):
    def _chunk_bytes(source: bytes, size: int) -> Generator[bytes, None, None]:
        for index in range(0, len(source), size):
            yield source[index : index + size]

    manifest_asset: Path = next(_data.BASE_PATH.iterdir())
    manifest = _data.build_manifest(release_tag, *[manifest_asset])

    # here we are inserting the /test directory between the asset and the actual
    # temporary directory to ensure that we are testing that the download_data will
    # create missing parent directories if necessary
    manifest_key = list(manifest.keys())[0]
    manifest_key_path = Path(manifest_key)
    manifest_testing_key = (
        manifest_key_path.parent.joinpath("test")
        .joinpath(manifest_key_path.name)
        .as_posix()
    )

    # forceably update the current manifest asset key with the new testing key to test
    # parent directory creation
    manifest[manifest_testing_key] = manifest[manifest_key]
    del manifest[manifest_key]

    with TemporaryDirectory(prefix="facelift-test") as temp_dir, NamedTemporaryFile(
        dir=temp_dir
    ) as temp_file:
        temp_dirpath = Path(temp_dir)
        temp_filepath = Path(temp_file.name)
        shutil.copy(manifest_asset, temp_filepath)

        with patch(
            "facelift._data.get_remote_manifest"
        ) as mocked_get_remote_manifest, patch(
            "facelift._data._download"
        ) as mocked_download, patch(
            "facelift._data.BASE_PATH", temp_dirpath
        ):
            mocked_get_remote_manifest.return_value = manifest
            with temp_filepath.open("rb") as file_handle:
                mocked_download.return_value = _chunk_bytes(
                    file_handle.read(), _data.DOWNLOAD_CHUNK_SIZE
                )

            _data.download_data(validate=True)
            assert temp_dirpath.joinpath(manifest_testing_key).is_file()

            with manifest_asset.open("rb") as manifest_file_handle, temp_filepath.open(
                "rb"
            ) as temp_file_handle:
                assert (
                    md5(manifest_file_handle.read()).digest()
                    == md5(temp_file_handle.read()).digest()
                )
