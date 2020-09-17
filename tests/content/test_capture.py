# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains tests for the content frame capture logic."""

from pathlib import Path
from typing import Any, Tuple
from unittest.mock import MagicMock, patch

import cv2
import pytest
from hypothesis import given
from hypothesis.strategies import just, one_of, sampled_from, tuples

from facelift.content.capture import (
    _iter_capture,
    file_capture,
    iter_media_frames,
    iter_stream_frames,
    media_capture,
    stream_capture,
)
from facelift.content.types import MediaType

from ..strategies import builtin_types, pathlib_path
from .strategies import image_path, media, video_path


@given(builtin_types(exclude=[int]), just(MediaType.STREAM))
def test_media_capture_asserts_media_streams_are_integers(
    media: Any, media_type: MediaType
):
    with pytest.raises(AssertionError):
        with media_capture(media, media_type):
            pass


@given(builtin_types(exclude=[str]), sampled_from([MediaType.IMAGE, MediaType.VIDEO]))
def test_media_capture_asserts_media_files_are_strings(
    media: Any, media_type: MediaType
):
    with pytest.raises(AssertionError):
        with media_capture(media, media_type):
            pass


@given(media())
def test_media_capture(media: Tuple[Path, MediaType]):
    with patch("facelift.content.capture.cv2.VideoCapture") as mocked_cv2_VideoCapture:
        media_filepath, media_type = media
        with media_capture(media_filepath.as_posix(), media_type) as capture:
            mocked_cv2_VideoCapture.assert_called_once_with(media_filepath.as_posix())

        capture.release.assert_called()


@given(media())
def test_media_capture_raises_ValueError_on_failure_to_open_capture(
    media: Tuple[Path, MediaType]
):
    media_filepath, media_type = media
    with patch("facelift.content.capture.cv2.VideoCapture") as mocked_cv2_VideoCapture:
        mocked_cv2_VideoCapture.return_value = None

        with pytest.raises(ValueError):
            with media_capture(media_filepath.as_posix(), media_type):
                pass

    with patch("facelift.content.capture.cv2.VideoCapture") as mocked_cv2_VideoCapture:
        mock_VideoCapture = MagicMock()
        mock_VideoCapture.isOpened.return_value = False
        mocked_cv2_VideoCapture.return_value = mock_VideoCapture

        with pytest.raises(ValueError):
            with media_capture(media_filepath.as_posix(), media_type):
                pass


@given(pathlib_path())
def test_file_capture_raises_FileNotFoundError_on_missing_filepath(filepath: Path):
    with pytest.raises(FileNotFoundError):
        with file_capture(filepath):
            pass


@given(just(Path(__file__)))
def test_file_capture_raises_ValueError_on_unhandled_mediatype(filepath: Path):
    with patch("facelift.content.capture.get_media_type") as mocked_get_media_type:
        mocked_get_media_type.return_value = None

        with pytest.raises(ValueError):
            with file_capture(filepath):
                pass


@given(image_path())
def test_file_capture_yields_image_media_capture(filepath: Path):
    with patch(
        "facelift.content.capture.media_capture", wraps=media_capture
    ) as mocked_media_capture:

        with file_capture(filepath):
            pass

        mocked_media_capture.assert_called_once_with(
            filepath.as_posix(), MediaType.IMAGE
        )


@given(video_path())
def test_file_capture_yields_video_media_capture(filepath: Path):
    with patch(
        "facelift.content.capture.media_capture", wraps=media_capture
    ) as mocked_media_capture:
        with file_capture(filepath):
            pass

        mocked_media_capture.assert_called_once_with(
            filepath.as_posix(), MediaType.VIDEO
        )
