# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains helpers and managers for capturing content from various sources."""

from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional, Union

import cv2
import numpy

from .magic import get_media_type
from .types import Frame, MediaType


@contextmanager
def media_capture(
    media: Union[str, int], media_type: MediaType
) -> Generator[cv2.VideoCapture, None, None]:
    """General purpose media capture context manager.

    This context manager is basically just a wrapper around the provided
    :class:`~cv2.VideoCapture` constructor along with some capturing destruction logic.
    The provided ``media`` can either be a filepath to capture frames off of or a device
    id as defined by the `OpenCV video IO enum <https://bit.ly/3cctIN8>`_.

    In most all cases where you just want to build a capture off of your default webcam,
    you should just be giving a ``media`` of ``0``.

    Args:
        media (Union[str, int]): The media to build a capturer for

    Raises:
        ValueError: On failure to open the given media for capture

    Yields:
        cv2.VideoCapture: A capturer that allows for reading subsequential frames
    """

    if media_type == MediaType.STREAM:
        assert isinstance(media, int) and not isinstance(media, bool), (
            "media stream capture must specify an integer device id or stream type, "
            f"received {media!r}"
        )
    elif media_type in (MediaType.IMAGE, MediaType.VIDEO):
        assert isinstance(
            media, str
        ), f"media file capture must specifify a string file path, received {media!r}"

    capture: Optional[cv2.VideoCapture] = None  # pragma: no cover
    try:
        capture = cv2.VideoCapture(media)
        if capture is None or not capture.isOpened():
            raise ValueError(f"Failed to open capture for media at {media!r}")

        yield capture
    finally:
        if capture is not None:
            capture.release()


@contextmanager
def file_capture(filepath: Path) -> Generator[cv2.VideoCapture, None, None]:
    """Context manager to open a given filepath for frame capture.

    Args:
        filepath (Path): The filepath to open for capture

    Raises:
        FileNotFoundError: When the given filepath doesn't exist
        ValueError: When the given filepath is not of a supported media type

    Yields:
        cv2.VideoCapture: A capturer that allows for reading frames from the given media
            filepath
    """

    if not filepath.is_file():
        raise FileNotFoundError(f"No such file {filepath!s} exists")

    media_type = get_media_type(filepath)
    if not media_type:
        raise ValueError(f"Unsupported media type from {filepath!s}")

    with media_capture(filepath.as_posix(), media_type) as capture:
        yield capture


@contextmanager
def stream_capture(
    stream_type: Optional[int] = None,
) -> Generator[cv2.VideoCapture, None, None]:
    """Context manager to open a stream for frame capture.

    By default this context manager will just attempt to connect to open capturing on
    any available webcams or connected cameras.
    You can get more specific about what device you would like to open a capturer on by
    supplying a different stream type.
    These stream types come directly from the
    `OpenCV video IO enum <https://bit.ly/3cctIN8>`_.

    Args:
        stream_type (Optional[int], optional): The stream type to open

    Raises:
        ValueError: When the given stream device fails to be opened for capture

    Yields:
        cv2.VideoCapture: A capturer that allows for reading frames from the defined
            stream type
    """

    capture_index = stream_type or cv2.CAP_ANY
    try:
        with media_capture(capture_index, MediaType.STREAM) as capture:
            yield capture
    except ValueError as exc:
        raise ValueError(
            f"Failed to open device {capture_index!r} for capture"
        ) from exc


def _iter_capture(capture: cv2.VideoCapture) -> Generator[Frame, None, None]:
    """Iterate over available frames from the given capture.

    Args:
        capture (cv2.VideoCapture): The capture to read and yield frames from

    Yields:
        Frame: A read frame from the given capture
    """

    read_success = True
    while read_success:  # pragma: no cover
        read_success, frame = capture.read()
        if not read_success or not isinstance(frame, numpy.ndarray):
            break

        yield frame


def iter_media_frames(media_filepath: Path) -> Generator[Frame, None, None]:
    """Iterate over frames from a given supported media file.

    Args:
        media_filepath (Path): The filepath to the media to read frames from

    Yields:
        Frame: A read frame from the given media file
    """

    with file_capture(media_filepath) as capture:
        yield from _iter_capture(capture)


def iter_stream_frames(
    stream_type: Optional[int] = None,
) -> Generator[Frame, None, None]:  # pragma: no cover
    """Iterate over frames from a given streaming device.

    By default this iterator will attempt to connect to the first available webcam and
    yield the webcam's streamed frames.
    You can specifiy the appropriate device index 0-99 (0 being the default), or a
    custom stream type defined by the `OpenCV video IO enum <https://bit.ly/3cctIN8>`_.

    Args:
        stream_type (Optional[int], optional): The stream type to attempt to open.

    Yields:
        Frame: A read frame from the given streaming device
    """

    with stream_capture(stream_type) as capture:
        yield from _iter_capture(capture)
