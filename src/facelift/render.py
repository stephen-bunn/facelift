# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains some very basic wrappers around drawing things onto frames.

When detecting faces, it is kinda nice to be able to see what features are being
detected and where inaccuracies are being detected.
With a combination of the :mod:`~.window` module and some of these helper functions, we
can easily visualize what features are being detected.

For example, if we wanted to draw lines for each detected feature from the
:class:`~.detect.PartialFaceDetector` we can do the following:

>>> from facelift.capture import iter_stream_frames
>>> from facelift.window import opencv_window
>>> from facelift.detect import PartialFaceDetector
>>> from facelift.render import draw_line
>>> detector = PartialFaceDetector()
>>> with opencv_window() as window:
...     for frame in iter_stream_frames():
...         for face in detector.iter_faces(frame):
...             for _, points in face.landmarks.items():
...                 frame = draw_line(frame, points)
...         window.render(frame)

Attributes:
    DEFAULT_COLOR (Tuple[int, int, int]):
        The default color for all draw helper functions.
        Defaults to (255, 255, 255), or white.
    DEFAULT_FONT (int):
        The default OpenCV HERSHEY font to use for rendering text.
        Defaults to ``cv2.FONT_HERSHEY_SIMPLEX``
"""

from enum import Enum, IntEnum
from typing import List, Optional, Tuple

import cv2
import numpy

from .types import Frame, Point, PointSequence

DEFAULT_COLOR = (255, 255, 255)
DEFAULT_FONT = cv2.FONT_HERSHEY_SIMPLEX


class LineType(IntEnum):
    """Enumeration of the different available PointSequence types for OpenCV.

    Attributes:
        FILLED:
            Filled line (useful for single points).
        CONNECTED_4:
            A 4-point connected line.
        CONNECTED_8:
            An 8-point connected line.
        ANTI_ALIASED:
            An anti-aliased line (good for drawing curves).
    """

    FILLED = cv2.FILLED
    CONNECTED_4 = cv2.LINE_4
    CONNECTED_8 = cv2.LINE_8
    ANTI_ALIASED = cv2.LINE_AA


class Position(Enum):
    """Enumeration of available relative positions.

    Attributes:
        START:
            Positioned content appears at the left of the container.
        END:
            Positioned content appears at the right of the container.
        CENTER:
            Positioned content appears in the middle of the container.
    """

    START = "start"
    END = "end"
    CENTER = "center"


def _get_positioned_index(
    index: int,
    container_size: int,
    content_size: int,
    position: Position,
    offset: Optional[int] = None,
) -> int:
    """Build the appropriate index for positioning some content in some container size.

    Args:
        index (int):
            The starting index of the content to be positioned within a container size.
        container_size (int):
            The total size of the container we are trying to position content within.
        content_size (int):
            The size of the content we are attempting to place within the container.
        position (:class:`~.render.Position`):
            The position we are using to place contin within the container.
        offset (Optional[int], optional):
            An optional offset to apply to the built positioned index.
            Defaults to None.

    Returns:
        int:
            The built index for the content to be placed within the container size.
    """

    base_index = index
    if position == Position.CENTER:
        base_index += (container_size - content_size) // 2
    elif position == Position.END:
        base_index += container_size

    return base_index + (offset or 0)


def draw_point(
    frame: Frame,
    point: Point,
    size: int = 1,
    color: Tuple[int, int, int] = DEFAULT_COLOR,
    thickness: int = -1,
    line_type: LineType = LineType.FILLED,
) -> Frame:
    """Draw a single point on a given frame.

    Examples:
        Draw a single point a position (10, 10) on a given frame.

        >>> from facelift.render import draw_point
        >>> frame = draw_point(frame, (10, 10))

    Args:
        frame (:attr:`~.types.Frame`):
            The frame to draw the point
        point (:attr:`~.types.Point`):
            The pixel coordinates to draw the point
        size (int, optional):
            The size of the point.
            Defaults to 1.
        color (Tuple[int, int, int], optional):
            The color of the point.
            Defaults to DEFAULT_COLOR.
        thickness (int, optional):
            The thickness of the point.
            Defaults to -1.
        line_type (LineType, optional):
            The type of line type to use for the point.
            Defaults to LineType.FILLED.

    Returns:
        :attr:`~.types.Frame` The frame with the point drawn on it
    """

    cv2.circle(
        img=frame,
        center=tuple(point),
        radius=size,
        color=color,
        thickness=thickness,
        lineType=line_type.value,
    )

    return frame


def draw_points(
    frame: Frame,
    points: PointSequence,
    size: int = 1,
    color: Tuple[int, int, int] = DEFAULT_COLOR,
    thickness: int = -1,
    line_type: LineType = LineType.FILLED,
) -> Frame:
    """Draw multiple points on a given frame.

    Examples:
        Draw a sequence of points to a given frame.

        >>> from facelift.render import draw_points
        >>> frame = draw_points(frame, [(10, 10), (20, 20)])

    Args:
        frame (:attr:`~.types.Frame`):
            The frame to draw the points on.
        points (:attr:`~.types.PointSequence`):
            The sequence of points to draw.
        size (int, optional):
            The size of the points.
            Defaults to 1.
        color (Tuple[int, int, int], optional):
            The color of the points.
            Defaults to DEFAULT_COLOR.
        thickness (int, optional):
            The thickness of the points.
            Defaults to -1.
        line_type (LineType, optional):
            The type of line type to use for the points.
            Defaults to LineType.FILLED.

    Returns:
        :attr:`~.types.Frame` The frame with the points drawn on it
    """

    for point in points:
        frame = draw_point(
            frame,
            point,
            size=size,
            color=color,
            thickness=thickness,
            line_type=line_type,
        )
    return frame


def draw_line(
    frame: Frame,
    line: PointSequence,
    sequence: Optional[List[Tuple[int, int]]] = None,
    color: Tuple[int, int, int] = DEFAULT_COLOR,
    thickness: int = 1,
    line_type: LineType = LineType.ANTI_ALIASED,
) -> Frame:
    """Draw a sequence of connected points on a given frame.

    Examples:
        Draw a line between a sequence of points.

        >>> from facelift.render import draw_line
        >>> frame = draw_line(frame, [(10, 10), (20, 20)])

    Args:
        frame (:attr:`~.types.Frame`):
            The frame to draw the line on.
        line (:attr:`~.types.PointSequence`):
            The array of points to draw on the given frame
        sequence (Optional[List[Tuple[int, int]]], optional):
            An optional custom sequence for drawing the given line points.
            Defaults to None.
        color (Tuple[int, int, int], optional):
            The color of the line.
            Defaults to DEFAULT_COLOR.
        thickness (int, optional):
            The thickness of the line. Defaults to 1.
        line_type (LineType, optional):
            The type of the line.
            Defaults to LineType.FILLED.

    Returns:
        :attr:`~.types.Frame` The frame with the line drawn on it
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
    line: PointSequence,
    color: Tuple[int, int, int] = DEFAULT_COLOR,
    thickness: int = -1,
    line_type: LineType = LineType.ANTI_ALIASED,
) -> Frame:
    """Form and draw a contour for the given line on a frame.

    Examples:
        Draw a contour between multiple points.

        >>> from facelift.render import draw_contour
        >>> frame = draw_contour(frame, [(10, 10), (20, 20)])

    Args:
        frame (:attr:`~.types.Frame`):
            The frame to draw the contour on.
        line (:attr:`~.types.PointSequence`):
            The array of points to use to form the contour.
        color (Tuple[int, int, int], optional):
            The color of the contour..
            Defaults to DEFAULT_COLOR.
        thickness (int, optional):
            The thickness of the contour.
            Defaults to -1.
        line_type (LineType, optional):
            The line type to use for the contour.
            Defaults to LineType.ANTI_ALIASED.

    Returns:
        :attr:`~.types.Frame` The frame with the contour drawn on it
    """

    if isinstance(line, list):
        line = numpy.asarray(line)

    convex_hull = cv2.convexHull(points=line.astype("int32"))  # type: ignore
    cv2.drawContours(
        image=frame,
        contours=[convex_hull],
        contourIdx=-1,
        color=color,
        thickness=thickness,
        lineType=line_type.value,
    )

    return frame


def draw_rectangle(
    frame: Frame,
    start: Point,
    end: Point,
    color: Tuple[int, int, int] = DEFAULT_COLOR,
    thickness: int = 1,
    line_type: LineType = LineType.ANTI_ALIASED,
) -> Frame:
    """Draw a rectangle on the given frame.

    Examples:
        Draw a rectangle starting at (10, 10) and ending at (20, 20).

        >>> from facelift.render import draw_rectangle
        >>> frame = draw_rectangle(frame, (10, 10), (20, 20))

    Args:
        frame (:attr:`~.types.Frame`):
            The frame to draw the rectangle on.
        start (:attr:`~.types.Point`):
            The starting point of the rectangle.
        end (:attr:`~.types.Point`):
            The ending point of the rectangle.
        color (Tuple[int, int, int], optional):
            The color of the rectangle.
            Defaults to DEFAULT_COLOR.
        thickness (int, optional):
            The thickness of the rectangle.
            Defaults to 1.
        line_type (LineType, optional):
            The line type to use when drawing the lines of the rectangle.
            Defaults to LineType.ANTI_ALIASED.

    Returns:
        :attr:`~.types.Frame` The frame with the rectangle drawn on it
    """

    cv2.rectangle(
        img=frame,
        pt1=tuple(start),
        pt2=tuple(end),
        color=color,
        thickness=thickness,
        lineType=line_type,
    )

    return frame


def draw_text(
    frame: Frame,
    text: str,
    start: Point,
    end: Point,
    color: Tuple[int, int, int] = DEFAULT_COLOR,
    font: int = DEFAULT_FONT,
    font_scale: float = 1,
    thickness: int = 1,
    line_type: LineType = LineType.ANTI_ALIASED,
    x_position: Position = Position.START,
    y_position: Position = Position.START,
    x_offset: int = 0,
    y_offset: int = 0,
    allow_overflow: bool = False,
) -> Frame:
    """Draw some text on the given frame.

    Examples:
        Draw the text "Hello, World!" right-aligned within the text rectangle from
        (10, 10) to (20, 20).

        >>> from facelift.render import draw_text, Position
        >>> frame = draw_text(
        ...     frame,
        ...     "Hello, World",
        ...     (10, 10),
        ...     (20, 20),
        ...     x_position=Position.END
        ... )

    Args:
        frame (:attr:`~.types.Frame`):
            The frame to draw some text on
        text (str):
            The text to draw on the frame
        start (:attr:`~.types.Point`):
            The starting point of the text container
        end (:attr:`~.types.Point`):
            The ending point of the text container
        color (Tuple[int, int, int], optional):
            The color of the text.
            Defaults to DEFAULT_COLOR.
        font (int, optional):
            The OpenCV hershey font to draw the text with.
            Defaults to DEFAULT_FONT.
        font_scale (float, optional):
            The scale of the font.
            Defaults to 1.
        thickness (int, optional):
            The thickness of the font.
            Defaults to 1.
        line_type (LineType, optional):
            The line type of the font.
            Defaults to LineType.ANTI_ALIASED.
        x_position (Position, optional):
            The x-axis position to draw the text in relative to the text container.
            Defaults to Position.START.
        y_position (Position, optional):
            The y-axis position to draw the text in relative to the text container.
            Defaults to Position.START.
        x_offset (int, optional):
            The x-axis offset from the text container to add to the calculated relative
            position.
            Defaults to 0.
        y_offset (int, optional):
            The y-axis offset from the text container to add to the calculated relative
            position.
            Defaults to 0.
        allow_overflow (bool, optional):
            If set to ``True``, the provided text will start drawing at the given start
            and end points without obeying them as a bounding text container.
            Defaults to False.

    Returns:
        :attr:`~.types.Frame` The frame with the text drawn on it
    """

    if len(text) <= 0:
        return frame

    start_x, start_y = tuple(start)
    end_x, end_y = tuple(end)

    width = end_x - start_x
    height = end_y - start_y

    text_width, text_height = cv2.getTextSize(
        text=text,
        fontFace=font,
        fontScale=font_scale,
        thickness=thickness,
    )[0]

    # handle constraining the text to the given bounding container
    if not allow_overflow:
        if y_position == Position.START:
            y_offset += text_height
        if x_position == Position.END:
            x_offset -= text_width

    # handle offsetting by the text's height if we are attempting to center vertically
    if y_position == Position.CENTER:
        y_offset += text_height

    text_x = _get_positioned_index(
        index=start_x,
        container_size=width,
        content_size=text_width,
        position=x_position,
        offset=x_offset,
    )
    text_y = _get_positioned_index(
        index=start_y,
        container_size=height,
        content_size=text_height,
        position=y_position,
        offset=y_offset,
    )

    cv2.putText(
        img=frame,
        text=text,
        org=(text_x, text_y),
        fontFace=font,
        fontScale=font_scale,
        color=color,
        thickness=thickness,
        lineType=line_type.value,
    )

    return frame
