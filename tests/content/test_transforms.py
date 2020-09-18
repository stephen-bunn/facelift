# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""
"""

from unittest.mock import patch

import cv2
import pytest
from hypothesis import given
from hypothesis.strategies import floats, integers, just, sampled_from

from facelift.content import transforms
from facelift.content.types import Frame

from .strategies import frame


@given(frame())
def test_copy(frame: Frame):
    copied_frame = transforms.copy(frame)
    assert (frame == copied_frame).all()
    assert frame is not copied_frame


@given(frame(), floats(max_value=0))
def test_scale_raises_ValueError_with_non_positive_factor(frame: Frame, factor: float):
    with pytest.raises(ValueError):
        transforms.scale(frame, factor)


@given(frame())
def test_scale_returns_same_frame_with_default_factor(frame: Frame):
    transformed_frame = transforms.scale(frame, 1)
    assert (frame == transformed_frame).all()
    assert frame is transformed_frame


@given(
    frame(width_strategy=just(1), height_strategy=just(1)),
    floats(min_value=0.1, max_value=0.9),
)
def test_scale_returns_same_frame_with_too_small_frame(frame: Frame, factor: float):
    transformed_frame = transforms.scale(frame, factor)
    assert (frame == transformed_frame).all()
    assert frame is transformed_frame


@given(
    frame(width_strategy=just(256), height_strategy=just(256)),
    floats(min_value=0.1, max_value=2.0).filter(lambda value: value != 1.0),
)
def test_scale(frame: Frame, factor: float):
    height, width, *_ = frame.shape
    transformed_frame = transforms.scale(frame, factor)
    transformed_height, transformed_width, *_ = transformed_frame.shape

    assert frame is not transformed_frame
    assert transformed_height == round(height * factor)
    assert transformed_width == round(width * factor)


@given(frame())
def test_resize_raises_ValueError_for_height_or_width_of_zero(frame: Frame):
    with pytest.raises(ValueError):
        transforms.resize(frame, height=0)

    with pytest.raises(ValueError):
        transforms.resize(frame, width=0)


@given(frame())
def test_resize_returns_same_frame_with_no_width_and_height(frame: Frame):
    transformed_frame = transforms.resize(frame)
    assert (frame == transformed_frame).all()
    assert frame is transformed_frame


@given(
    frame(), integers(min_value=1, max_value=256), integers(min_value=1, max_value=256)
)
def test_resize_returns_exact_sized_frame_with_width_and_height(
    frame: Frame, width: int, height: int
):
    transformed_frame = transforms.resize(frame, width=width, height=height)
    transformed_height, transformed_width, *_ = transformed_frame.shape

    assert transformed_width == width
    assert transformed_height == height
    assert transformed_frame is not frame


@given(frame(), integers(min_value=1, max_value=256))
def test_resize_returns_one_sized_frame_when_lock_aspect_disabled(
    frame: Frame, size: int
):
    height, width, *_ = frame.shape
    transformed_width_frame = transforms.resize(frame, width=size, lock_aspect=False)
    (
        transformed_width_height,
        transformed_width_width,
        *_,
    ) = transformed_width_frame.shape

    assert transformed_width_width == size
    assert transformed_width_height == height
    assert transformed_width_frame is not frame

    transformed_height_frame = transforms.resize(frame, height=size, lock_aspect=False)
    (
        transformed_height_height,
        transformed_height_width,
        *_,
    ) = transformed_height_frame.shape

    assert transformed_height_width == width
    assert transformed_height_height == size
    assert transformed_height_frame is not frame


@given(frame(), integers(min_value=1, max_value=256))
def test_resize_returns_relative_sized_frame(frame: Frame, size: int):
    height, width, *_ = frame.shape
    transformed_width_frame = transforms.resize(frame, width=size)
    (
        transformed_width_height,
        transformed_width_width,
        *_,
    ) = transformed_width_frame.shape

    assert transformed_width_width == size
    assert transformed_width_height == int(height * (size / float(width))) or 1
    assert transformed_width_frame is not frame

    transformed_height_frame = transforms.resize(frame, height=size)
    (
        transformed_height_height,
        transformed_height_width,
        *_,
    ) = transformed_height_frame.shape

    assert transformed_height_width == int(width * (size / float(height))) or 1
    assert transformed_height_height == size
    assert transformed_height_frame is not frame


@given(frame(), sampled_from([0, 360, -360]))
def test_rotate_returns_same_frame_with_no_rotation(frame: Frame, degrees: int):
    transformed_frame = transforms.rotate(frame, degrees)
    assert (transformed_frame == frame).all()
    assert transformed_frame is frame


@given(frame(), sampled_from([90, 180, 270]))
def test_rotate(frame: Frame, degrees: int):
    # TODO: this test is very naive and doesn't actually test functionality
    transformed_frame = transforms.rotate(frame, degrees)
    assert transformed_frame is not frame


@given(frame())
def test_translate_returns_same_frame_with_no_delta(frame: Frame):
    transformed_frame = transforms.translate(frame)
    assert (transformed_frame == frame).all()
    assert transformed_frame is frame


@given(frame(), integers(min_value=-256, max_value=256))
def test_translate(frame: Frame, delta: int):
    # TODO: this test is very naive and doesn't actually test functionality
    transformed_frame = transforms.translate(frame, delta_x=delta)
    assert transformed_frame is not frame


@given(frame())
def test_grayscale(frame: Frame):
    with patch("facelift.content.transforms.cv2.cvtColor") as mocked_cv2_cvtColor:
        transforms.grayscale(frame)

    mocked_cv2_cvtColor.assert_called_once_with(src=frame, code=cv2.COLOR_BGR2GRAY)


@given(frame())
def test_rgb(frame: Frame):
    with patch("facelift.content.transforms.cv2.cvtColor") as mocked_cv2_cvtColor:
        transforms.rgb(frame)

    mocked_cv2_cvtColor.assert_called_once_with(src=frame, code=cv2.COLOR_BGR2RGB)
