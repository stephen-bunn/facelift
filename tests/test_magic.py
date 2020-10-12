# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains tests for testing the content magic module."""

import os
import sys
import tempfile
from pathlib import Path
from typing import List, Tuple
from unittest.mock import patch

import pytest
from hypothesis import assume, given
from hypothesis.strategies import text

from facelift import magic
from facelift.types import MediaType

from .strategies import media_details, pathlib_path


@given(pathlib_path())
def test_get_mimetype_raises_FileNotFoundError_on_invalid_filepaths(filepath: Path):
    assume(filepath.exists() == False)

    with pytest.raises(FileNotFoundError):
        magic.get_mimetype(filepath)


@given(media_details())
def test_get_mimetype_returns_correct_mimetype(
    media_details: Tuple[str, str, List[str], bytes]
):
    _, _, mimetypes, buffer = media_details
    try:
        file_descriptor, filename = tempfile.mkstemp()
        with open(file_descriptor, "wb") as temp_fp:
            temp_fp.write(buffer)

        assert magic.get_mimetype(Path(filename)) in mimetypes
    finally:
        os.remove(filename)


@given(pathlib_path())
def test_get_media_type_raises_FileNotFoundError_on_invalid_filepaths(filepath: Path):
    assume(filepath.exists() == False)

    with pytest.raises(FileNotFoundError):
        magic.get_media_type(filepath)


def test_get_media_type_returns_None_for_files_with_no_guessable_mimetype():
    with patch.object(magic, "get_mimetype") as mocked_get_mimetype:
        mocked_get_mimetype.return_value = None

        # since we are mocking get_mimetype, the given media_filepath doesn't matter
        assert magic.get_media_type(None) is None


@given(media_details())
def test_get_media_type_returns_correct_media_type(
    media_details: Tuple[str, str, List[str], bytes]
):
    name, media_type, _, buffer = media_details
    try:
        file_descriptor, filename = tempfile.mkstemp()
        with open(file_descriptor, "wb") as temp_fp:
            temp_fp.write(buffer)

        assert magic.get_media_type(Path(filename)) == MediaType(media_type)
    finally:
        os.remove(filename)


@given(text(), text())
def test_get_media_type_returns_None_for_no_validate(prefix: str, suffix: str):
    assume(prefix not in map(str, MediaType))
    invalid_mimetype = f"{prefix!s}/{suffix!s}"

    with patch.object(magic, "get_mimetype") as mocked_get_mimetype:
        mocked_get_mimetype.return_value = invalid_mimetype

        assert magic.get_media_type(Path.cwd(), validate=False) is None


@given(text(), text())
def test_get_media_type_raises_ValueError_for_validate(prefix: str, suffix: str):
    assume(prefix not in map(str, MediaType))
    invalid_mimetype = f"{prefix!s}/{suffix!s}"

    with patch.object(magic, "get_mimetype") as mocked_get_mimetype:
        mocked_get_mimetype.return_value = invalid_mimetype

        with pytest.raises(ValueError):
            magic.get_media_type(Path.cwd(), validate=True)
