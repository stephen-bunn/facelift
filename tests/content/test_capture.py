# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains tests for the content frame capture logic."""

from pathlib import Path
from typing import Any, Optional, Tuple
from unittest.mock import MagicMock, patch

import cv2
import numpy
import pytest
from hypothesis import given
from hypothesis.strategies import integers, just, none, one_of, sampled_from

from facelift.content.capture import (
    file_capture,
    iter_media_frames,
    media_capture,
    stream_capture,
)
from facelift.types import MediaType

from ..strategies import builtin_types, image_path, media, pathlib_path, video_path


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


def test_stream_capture_default():
    with patch("facelift.content.capture.media_capture") as mocked_media_capture:
        with stream_capture():
            pass

        mocked_media_capture.assert_called_once_with(0, MediaType.STREAM)


@given(integers(min_value=0, max_value=99))
def test_stream_capture_custom_stream_type(stream_type: int):
    with patch("facelift.content.capture.media_capture") as mocked_media_capture:
        with stream_capture(stream_type):
            pass

        mocked_media_capture.assert_called_once_with(stream_type, MediaType.STREAM)


@given(one_of(none(), integers(min_value=0, max_value=99)))
def test_stream_capture_raises_ValueError_on_failure_to_open_device(
    stream_type: Optional[int],
):
    with patch("facelift.content.capture.media_capture") as mocked_media_capture:
        mocked_media_capture.side_effect = ValueError

        with pytest.raises(ValueError):
            with stream_capture(stream_type):
                pass


@given(one_of(image_path(), video_path()))
def test_iter_media_frames(media_filepath: Path):
    assert all(
        isinstance(frame, numpy.ndarray) for frame in iter_media_frames(media_filepath)
    )


@given(image_path())
def test_iter_media_frames_attempts_to_loop(media_filepath: Path):
    mock_capture = MagicMock()
    with patch("facelift.content.capture.file_capture") as mocked_file_capture, patch(
        "facelift.content.capture._iter_capture"
    ) as mock_iter_capture:
        # mock the context manager's capture
        mocked_file_capture.return_value.__enter__.return_value = mock_capture
        # mock the iterators yield to break out of the infinite loop on the second
        # access. this is ok to do as we are using images which only have 1 frame to
        # consume anyway
        mock_iter_capture.side_effect = [[None], RuntimeError]

        # expect the defined RuntimeError to break out of the infinite loop
        with pytest.raises(RuntimeError):
            iterator = iter_media_frames(media_filepath, loop=True)
            # the first thing we get from the iterator is our [None]
            assert next(iterator) is None
            # the second time we are breaking out of the infinite loop with RuntimeError
            next(iterator)

        # with the second access to the iterator we should have attempted to reset the
        # capture's frame index
        mock_capture.set.assert_called_once_with(cv2.CAP_PROP_POS_FRAMES, 0)
