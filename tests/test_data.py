# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains tests related to the _data module."""

import json
import string
from typing import Dict, Optional
from unittest.mock import patch

from hypothesis import given
from hypothesis.strategies import dictionaries, none, one_of, text

from facelift import _data


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
