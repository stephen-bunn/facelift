# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains tests for our OpenCV drawing wrappers.

Since we really are not adding *that* much functionality to these wrappers, we are
mainly just ensuring that calls are made to OpenCV as expected.
We don't want things to change and break right under our feet.
"""

import string
from typing import Optional, Tuple
from unittest.mock import ANY, call, patch

import cv2
import numpy
from hypothesis import assume, given
from hypothesis.strategies import (
    SearchStrategy,
    booleans,
    composite,
    floats,
    integers,
    lists,
    none,
    one_of,
    sampled_from,
    text,
    tuples,
)

from facelift import render
from facelift.types import Frame, Point, PointSequence

from .strategies import MAX_POINT, frame, point, point_sequence

MAX_THICKNESS = 2 ^ 15 - 1


@composite
def color(
    draw,
    red_strategy: Optional[SearchStrategy[int]] = None,
    green_strategy: Optional[SearchStrategy[int]] = None,
    blue_strategy: Optional[SearchStrategy[int]] = None,
) -> SearchStrategy[Tuple[int, int, int]]:
    color_value_strategy = integers(min_value=0, max_value=255)
    return draw(
        tuples(
            blue_strategy if blue_strategy else color_value_strategy,
            green_strategy if green_strategy else color_value_strategy,
            red_strategy if red_strategy else color_value_strategy,
        )
    )


@given(
    integers(min_value=0),
    integers(min_value=0),
    integers(min_value=0),
    sampled_from(render.Position),
    one_of(integers(min_value=0), none()),
)
def test_get_positioned_index(
    index: int,
    container_size: int,
    content_size: int,
    position: render.Position,
    offset: Optional[int],
):
    index = render._get_positioned_index(
        index, container_size, content_size, position, offset
    )
    assert isinstance(index, int)


@given(
    frame(),
    point(),
    integers(min_value=0, max_value=MAX_POINT),
    color(),
    integers(min_value=-1, max_value=MAX_THICKNESS),
    sampled_from(render.LineType),
)
def test_draw_point(
    frame: Frame,
    point: Point,
    size: int,
    color: Tuple[int, int, int],
    thickness: int,
    line_type: render.LineType,
):
    with patch("facelift.render.cv2", wraps=cv2) as mocked_cv2:
        drawn_frame = render.draw_point(
            frame,
            point,
            size=size,
            color=color,
            thickness=thickness,
            line_type=line_type,
        )
        assert isinstance(drawn_frame, numpy.ndarray)

    mocked_cv2.circle.assert_called_once_with(
        img=frame,
        center=tuple(point),
        radius=size,
        color=color,
        thickness=thickness,
        lineType=line_type.value,
    )


@given(
    frame(),
    point_sequence(),
    integers(min_value=0, max_value=MAX_POINT),
    color(),
    integers(min_value=-1, max_value=MAX_THICKNESS),
    sampled_from(render.LineType),
)
def test_draw_points(
    frame: Frame,
    points: PointSequence,
    size: int,
    color: Tuple[int, int, int],
    thickness: int,
    line_type: render.LineType,
):
    circle_calls = []
    for point in points:
        circle_calls.append(
            call(
                img=frame,
                center=tuple(point),
                radius=size,
                color=color,
                thickness=thickness,
                lineType=line_type.value,
            )
        )

    with patch("facelift.render.cv2", wraps=cv2) as mocked_cv2:
        drawn_frame = render.draw_points(
            frame,
            points,
            size=size,
            color=color,
            thickness=thickness,
            line_type=line_type,
        )
        assert isinstance(drawn_frame, numpy.ndarray)

    mocked_cv2.circle.assert_has_calls(circle_calls)


@given(
    frame(),
    point_sequence(),
    color(),
    integers(min_value=1, max_value=MAX_THICKNESS),
    sampled_from(render.LineType).filter(lambda x: x != render.LineType.FILLED),
)
def test_draw_line(
    frame: Frame,
    line: PointSequence,
    color: Tuple[int, int, int],
    thickness: int,
    line_type: render.LineType,
):
    line_calls = []
    for (start, end) in [(index, index + 1) for index in range(len(line) - 1)]:
        line_calls.append(
            call(
                img=frame,
                pt1=tuple(line[start]),
                pt2=tuple(line[end]),
                color=color,
                thickness=thickness,
                lineType=line_type.value,
            )
        )

    with patch("facelift.render.cv2", wraps=cv2) as mocked_cv2:
        drawn_frame = render.draw_line(
            frame, line, color=color, thickness=thickness, line_type=line_type
        )
        assert isinstance(drawn_frame, numpy.ndarray)

    mocked_cv2.line.assert_has_calls(line_calls)


@given(
    frame(),
    point_sequence(min_size=2, max_size=2),
    color(),
    integers(min_value=1, max_value=MAX_THICKNESS),
    sampled_from(render.LineType).filter(lambda x: x != render.LineType.FILLED),
)
def test_draw_line_custom_sequence(
    frame: Frame,
    line: PointSequence,
    color: Tuple[int, int, int],
    thickness: int,
    line_type: render.LineType,
):
    sequence = [(-1, 0), (0, -1)]
    line_calls = [
        call(
            img=frame,
            pt1=tuple(line[start]),
            pt2=tuple(line[end]),
            color=color,
            thickness=thickness,
            lineType=line_type.value,
        )
        for start, end in sequence
    ]
    with patch("facelift.render.cv2", wraps=cv2) as mocked_cv2:
        drawn_frame = render.draw_line(
            frame,
            line,
            sequence=sequence,
            color=color,
            thickness=thickness,
            line_type=line_type,
        )
        assert isinstance(drawn_frame, numpy.ndarray)

    mocked_cv2.line.assert_has_calls(line_calls)


@given(
    frame(),
    one_of(
        point_sequence(min_size=2),
        lists(point(), min_size=2),
        lists(tuples(integers(0, MAX_POINT), integers(0, MAX_POINT)), min_size=2),
    ),
    color(),
    integers(min_value=-1, max_value=MAX_THICKNESS),
    sampled_from(render.LineType).filter(lambda x: x != render.LineType.FILLED),
)
def test_draw_contour(
    frame: Frame,
    line: PointSequence,
    color: Tuple[int, int, int],
    thickness: int,
    line_type: render.LineType,
):
    with patch("facelift.render.cv2", wraps=cv2) as mocked_cv2:
        drawn_frame = render.draw_contour(
            frame, line, color=color, thickness=thickness, line_type=line_type
        )
        assert isinstance(drawn_frame, numpy.ndarray)

    mocked_cv2.convexHull.assert_called_once()
    mocked_cv2.drawContours.assert_called_once_with(
        image=frame,
        contours=[ANY],
        contourIdx=-1,
        color=color,
        thickness=thickness,
        lineType=line_type.value,
    )


@given(
    frame(),
    point(),
    point(),
    color(),
    integers(min_value=0, max_value=MAX_THICKNESS),
    sampled_from(render.LineType).filter(lambda x: x != render.LineType.FILLED),
)
def test_draw_rectangle(
    frame: Frame,
    start: Point,
    end: Point,
    color: Tuple[int, int, int],
    thickness: int,
    line_type: render.LineType,
):
    with patch("facelift.render.cv2", wraps=cv2) as mocked_cv2:
        drawn_frame = render.draw_rectangle(
            frame, start, end, color=color, thickness=thickness, line_type=line_type
        )
        assert isinstance(drawn_frame, numpy.ndarray)

    mocked_cv2.rectangle.assert_called_once_with(
        img=frame,
        pt1=tuple(start),
        pt2=tuple(end),
        color=color,
        thickness=thickness,
        lineType=line_type.value,
    )


@given(frame(), point(), point())
def test_draw_text_returns_same_frame_if_empty_text(
    frame: Frame, start: Point, end: Point
):
    with patch("facelift.render.cv2", wraps=cv2) as mocked_cv2:
        drawn_frame = render.draw_text(frame, "", start, end)
        assert frame is drawn_frame

    mocked_cv2.putText.assert_not_called()


@given(
    frame(),
    text(alphabet=string.printable, min_size=1),
    point(integers(0, MAX_POINT - 1)),
    point(integers(1, MAX_POINT)),
    color(),
    floats(0, 10),
    integers(0, MAX_THICKNESS),
    sampled_from(render.LineType),
    sampled_from(render.Position),
    sampled_from(render.Position),
    booleans(),
)
def test_draw_text(
    frame: Frame,
    text: str,
    start: Point,
    end: Point,
    color: Tuple[int, int, int],
    font_scale: float,
    thickness: int,
    line_type: render.LineType,
    x_position: render.Position,
    y_position: render.Position,
    allow_overflow: bool,
):
    assume((end > start).all())  # type: ignore

    with patch("facelift.render.cv2", wraps=cv2) as mocked_cv2:
        drawn_frame = render.draw_text(
            frame,
            text,
            start,
            end,
            color=color,
            thickness=thickness,
            line_type=line_type,
            font_scale=font_scale,
            x_position=x_position,
            y_position=y_position,
            allow_overflow=allow_overflow,
        )
        assert isinstance(drawn_frame, numpy.ndarray)

    mocked_cv2.putText.assert_called_once_with(
        img=frame,
        text=text,
        org=(ANY, ANY),
        fontFace=ANY,
        fontScale=font_scale,
        color=color,
        thickness=thickness,
        lineType=line_type.value,
    )
