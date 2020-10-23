# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains some helper abstractions for OpenCV windows and frame rendering.

This collection of window helpers is just to help standardize and cleanup how to
interact with OpenCV window displays.
The :class:`~opencv_window` context manager is very easy to use for getting a quick
window for rendering frames as they are produced.

For example:

>>> from pathlib import Path
>>> from facelift.window import opencv_window
>>> from facelift.capture import iter_media_frames
>>> with opencv_window() as window:
...     for frame in iter_media_frames(Path("~/my-file.mp4")):
...         window.render(frame)

This context manager will produce a new window for rendering the frames read from
``my-file.mp4`` and will destroy the window once the context is exited.

I wouldn't recommend using this for any kind of production use; mostly the OpenCV window
is just useful for debugging.

Attributes:
    DEFAULT_WINDOW_TITLE (str):
        The default OpenCV window title if none is supplied.
        Defaults to "Facelift".
    DEFAULT_WINDOW_DELAY (int):
        The default number of milliseconds to wait between showing frames.
        Defaults to 1.
    DEFAULT_WINDOW_STEP_KEY (int):
        The default ASCII key index to use as the step key when step is enabled.
        Defaults to ``0x20`` (Space).
"""

from contextlib import AbstractContextManager
from types import TracebackType
from typing import Optional, Type

import attr
import cv2

from .types import Frame

DEFAULT_WINDOW_TITLE = "Facelift"
DEFAULT_WINDOW_DELAY = 1
DEFAULT_WINDOW_STEP_KEY = 0x20


class WindowStyle:
    """Object namespace of available OpenCV window styles.

    Attributes:
        DEFAULT (int):
            The default OpenCV window style.
        AUTOSIZE (int):
            Automatically fit window size on creation.
        GUI_NORMAL (int):
            Window with a basic GUI experience.
        GUI_EXPANDED (int):
            Window with an expanded GUI experience.
        FULLSCREEN (int):
            Window that displays frames fullscreen (full-canvas).
        FREE_RATIO (int):
            Window that allows for any window ratio.
        KEEP_RATIO (int):
            Window that maintains the original window ratio.
        OPENGL (int):
            Window rendered via OpenGL.
            May not work for some machines and will only work if OpenCV is compiled with
            GPU support.
    """

    DEFAULT = cv2.WINDOW_NORMAL
    AUTOSIZE = cv2.WINDOW_AUTOSIZE
    GUI_NORMAL = cv2.WINDOW_GUI_NORMAL
    GUI_EXPANDED = cv2.WINDOW_GUI_EXPANDED
    FULLSCREEN = cv2.WINDOW_FULLSCREEN
    FREE_RATIO = cv2.WINDOW_FREERATIO
    KEEP_RATIO = cv2.WINDOW_KEEPRATIO
    OPENGL = cv2.WINDOW_OPENGL

    # This property is currently just used for testing
    __all__ = [
        DEFAULT,
        AUTOSIZE,
        GUI_NORMAL,
        GUI_EXPANDED,
        FULLSCREEN,
        FREE_RATIO,
        KEEP_RATIO,
        OPENGL,
    ]


@attr.s
class opencv_window(AbstractContextManager):
    """Create an OpenCV window that closes once the context exits.

    Examples:
        Easy usage of OpenCV's provided window to display read frames from a webcam.

        >>> from facelift.window import opencv_window
        >>> with opencv_window() as window:
        ...     for frame in iter_stream_frames():
        ...         window.render(frame)

    Args:
        title (str):
            The title of the OpenCV window.
        style (int):
            The style of the OpenCV window.
        delay (float):
            The number of milliseconds to delay between displaying frames.
        step (bool):
            Flag that indicates if the window should wait for a press of the defined
            ``step_key`` before releasing the render call.
            Defaults to False.
        step_key (int):
            The ASCII integer index of the key to wait for press when ``step`` is True.
            Defaults to ``0x20`` (Space).

    Raises:
        ValueError: If the given window title is an empty string
        ValueError: If the given window delay is less or equal to 0
    """

    title: str = attr.ib(default=DEFAULT_WINDOW_TITLE)
    style: int = attr.ib(default=WindowStyle.DEFAULT)
    delay: float = attr.ib(default=DEFAULT_WINDOW_DELAY)
    step: bool = attr.ib(default=False)
    step_key: int = attr.ib(default=DEFAULT_WINDOW_STEP_KEY)

    @title.validator
    def _validate_title(self, attribute: attr.Attribute, value: str):
        """Validate the window context's title.

        Args:
            attribute (~attr.Attribute): The attribute containing the window's title
            value (str): The given value of the window title

        Raises:
            ValueError: If the title is an empty string
        """

        if not isinstance(value, str) or len(value) <= 0:
            raise ValueError(
                f"Window title must be a non-empty string, received {value!r}"
            )

    @delay.validator
    def _validate_delay(self, attribute: attr.Attribute, value: float):
        """Validate the window context's delay.

        Args:
            attribute (~attr.Attribute): The attribute containing the window's delay
            value (float): The given value of the window delay

        Raises:
            ValueError: If the delay is less than or equal to 0
        """

        if not isinstance(value, int) or value <= 0:
            raise ValueError(
                f"Window delay must be a non-zero value, received {value!r}"
            )

    def __enter__(self):
        """Initialize the context of the window."""

        self.create()
        return super().__enter__()

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        """Destroy the context of the window."""

        self.close()
        return super().__exit__(exc_type, exc_value, traceback)

    def create(self):
        """Create a new window with the current context's title and style."""

        cv2.namedWindow(winname=self.title, flags=self.style)

    def close(self):
        """Destroy the window with the current context's title."""

        cv2.destroyWindow(winname=self.title)

    def render(self, frame: Frame):
        """Render a given frame in the current window.

        Args:
            frame (:attr:`~.types.Frame`):
                The frame to render within the window
        """

        cv2.imshow(winname=self.title, mat=frame)
        cv2.waitKey(delay=self.delay)

        if self.step:
            while cv2.waitKey(delay=0) != self.step_key:
                continue
