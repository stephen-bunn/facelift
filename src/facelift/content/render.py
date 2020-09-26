# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains some very basic wrappers around utilizing OpenCV for frame display.

This is not recommended if you are building a product that needs to have event handling
or anything more complex than just displaying frames.
"""

from contextlib import AbstractContextManager
from enum import IntEnum
from types import TracebackType
from typing import Optional, Tuple, Type

import attr
import cv2

from .types import Frame, Line, Point

DEFAULT_COLOR = (255, 255, 255)
DEFAULT_WINDOW_TITLE = "Facelift"
DEFAULT_WINDOW_DELAY = 1
DEFAULT_WINDOW_STEP_KEY = 0x20


class LineType(IntEnum):
    """Enumeration of the different available line types for OpenCV."""

    FILLED = cv2.FILLED
    DASHED = cv2.LINE_4
    DOTTED = cv2.LINE_8
    ANTI_ALIASED = cv2.LINE_AA


def draw_point(
    frame: Frame,
    point: Point,
    size: int = 1,
    color: Tuple[int, int, int] = DEFAULT_COLOR,
    thickness: int = -1,
    line_type: LineType = LineType.FILLED,
) -> Frame:
    """Draw a single point on a given frame.

    Args:
        frame (Frame): The frame to draw the point
        point (Point): The pixel coordinates to draw the point
        size (int, optional): The size of the point. Defaults to 1.
        color (Tuple[int, int, int], optional): The color of the point.
            Defaults to DEFAULT_COLOR.
        thickness (int, optional): The thickness of the point. Defaults to -1.
        line_type (LineType, optional): The type of line type to use for the point.
            Defaults to LineType.FILLED.

    Returns:
        Frame: The frame with the point drawn on it
    """

    cv2.circle(
        img=frame,
        center=point,
        radius=size,
        color=color,
        thickness=thickness,
        lineType=line_type.value,
    )
    return frame


def draw_line(
    frame: Frame,
    line: Line,
    sequence: Optional[Line] = None,
    color: Tuple[int, int, int] = DEFAULT_COLOR,
    thickness: int = 1,
    line_type: LineType = LineType.FILLED,
) -> Frame:
    """Draw a sequence of connected points on a given frame.

    Args:
        frame (Frame): The frame to draw the line on
        line (Line): The array of points to draw on the given frame
        sequence (Optional[Line], optional): An optional custom sequence for drawing the
            given line points. Defaults to None.
        color (Tuple[int, int, int], optional): The color of the line.
            Defaults to DEFAULT_COLOR.
        thickness (int, optional): The thickness of the line. Defaults to 1.
        line_type (LineType, optional): The type of the line.
            Defaults to LineType.FILLED.

    Returns:
        Frame: The frame with the line drawn on it
    """

    if not sequence:
        sequence = [(index, index + 1) for index in range(len(line) - 1)]

    for (start, end) in sequence:
        cv2.line(
            img=frame,
            pt1=tuple(line[start]),
            pt2=tuple(line[end]),
            color=color,
            thickness=thickness,
            lineType=line_type.value,
        )

    return frame


def draw_contour(
    frame: Frame,
    line: Line,
    color: Tuple[int, int, int] = DEFAULT_COLOR,
    thickness: int = -1,
    line_type=LineType.FILLED,
) -> Frame:
    """Form and draw a contour for the given line on a frame.

    Args:
        frame (Frame): The frame to draw the contour on
        line (Line): THe array of poitns to use to form the contour
        color (Tuple[int, int, int], optional): The color ofthe contour.
            Defaults to DEFAULT_COLOR.
        thickness (int, optional): The thickness of the contour. Defaults to -1.
        line_type ([type], optional): The line type to use for the contour.
            Defaults to LineType.FILLED.

    Returns:
        Frame: The frame with the contour drawn on it
    """
    convex_hull = cv2.convexHull(points=line)
    cv2.drawContours(
        image=frame,
        contours=[convex_hull],
        contourIdx=-1,
        color=color,
        thickness=thickness,
        lineType=line_type.value,
    )

    return frame


class WindowType(IntEnum):
    """An enumeration of available OpenCV window types."""

    DEFAULT = cv2.WINDOW_NORMAL
    NORMAL = cv2.WINDOW_GUI_NORMAL
    EXPANDED = cv2.WINDOW_GUI_EXPANDED
    FULLSCREEN = cv2.WINDOW_FULLSCREEN
    FREE_RATIO = cv2.WINDOW_FREERATIO
    KEEP_RATIO = cv2.WINDOW_KEEPRATIO
    OPENGL = cv2.WINDOW_OPENGL


@attr.s
class opencv_window(AbstractContextManager):
    """Create the window context necessary to display frames in OpenCV.

    Args:
        title (str): The title of the created window
        type (WindowType): The type of window to create
        delay (float): The number of milliseconds to delay
        auto_step (bool): Flag that indicates if the window should automatically allow
            for the next render call to proceed unblocked. Defaults to True
        step_key (int): The integer index of the key to wait until preseed when steps
            are not allowed to proceed unblocked

    Yields:
        opencv_window: The context class that you can use for rendering frames
    """

    title: str = attr.ib(default=DEFAULT_WINDOW_TITLE)
    type: WindowType = attr.ib(default=WindowType.DEFAULT)
    delay: float = attr.ib(default=DEFAULT_WINDOW_DELAY)
    auto_step: bool = attr.ib(default=True)
    step_key: int = attr.ib(default=DEFAULT_WINDOW_STEP_KEY)

    def __enter__(self):
        """Initialize the state of the window."""

        self.create()
        return super().__enter__()

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ):
        """Destroy the state of the created window."""

        self.close()
        return super().__exit__(exc_type, exc_value, traceback)

    def create(self):
        """Create a new window with the context's title."""

        cv2.namedWindow(winname=self.title, flags=self.type.value)

    def close(self):
        """Close the current window using the context's title."""

        cv2.destroyWindow(winname=self.title)

    def render(self, frame: Frame):
        """Render a given frame in the current window.

        Args:
            frame (Frame): The frame to render within the window
        """

        cv2.imshow(winname=self.title, mat=frame)
        cv2.waitKey(delay=self.delay)

        if not self.auto_step:
            while cv2.waitKey(0) != self.step_key:
                continue
