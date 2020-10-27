# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains tests for landmark detection helper methods.

Many of the helper functions are so straightforward containing no branches that writing
tests seems a bit overkill. The included tests are simply ensuring that inputs and
outputs are expected types with generic value checks.

The only real functionality being tested here is that of
:func:`~.helpers.get_normalized_frame` as that is the only method that is used
externally of the :mod:`~.helpers` module.
"""

from pathlib import Path
from unittest.mock import ANY, patch

import cv2
import numpy
import pytest
from hypothesis import given, settings
from hypothesis.strategies import (
    SearchStrategy,
    composite,
    dictionaries,
    floats,
    integers,
    just,
    none,
    sampled_from,
)

from facelift.capture import iter_media_frames
from facelift.detect import BasicFaceDetector
from facelift.helpers import (
    DEFAULT_NORMALIZED_FACE_SIZE,
    DEFAULT_NORMALIZED_LEFT_EYE_POSTION,
    get_eye_angle,
    get_eye_center_position,
    get_eye_deltas,
    get_eye_distance,
    get_eye_positions,
    get_normalized_frame,
)
from facelift.types import Face, FaceFeature, Frame

from .strategies import face, frame, image_path, point_sequence


@composite
def face_with_eyes(draw, invert_features: bool = False) -> SearchStrategy[Face]:
    eye_features = [FaceFeature.LEFT_EYE, FaceFeature.RIGHT_EYE]
    return draw(
        face(
            frame_strategy=none(),
            landmarks_strategy=dictionaries(
                (
                    sampled_from(FaceFeature).filter(lambda ff: ff not in eye_features)
                    if invert_features
                    else sampled_from(eye_features)
                ),
                point_sequence(),
                min_size=2,
            ),
        )
    )


@given(face_with_eyes())
def test_get_eye_positions(test_face: Face):
    # XXX: this test is testing literal implementation.
    # I don't expect for the logic behind finding mean positions to ever change for
    # eyes, so I'm not super concerned about this ATM
    result = get_eye_positions(test_face)
    assert len(result) == 2
    assert (
        result[0]
        == test_face.landmarks[FaceFeature.LEFT_EYE]  # type: ignore
        .mean(axis=0)
        .astype("int")
    ).all()
    assert (
        result[1]
        == test_face.landmarks[FaceFeature.RIGHT_EYE]  # type: ignore
        .mean(axis=0)
        .astype("int")
    ).all()


@given(face_with_eyes(invert_features=True))
def test_get_eye_positions_raises_ValueError_if_missing_eye_landmarks(test_face: Face):
    with pytest.raises(ValueError):
        get_eye_positions(test_face)


@given(face_with_eyes())
def test_get_eye_center_position(test_face: Face):
    # XXX: There is not much we can test here other than explicit logic
    result = get_eye_center_position(test_face)
    assert len(result) == 2
    assert all(isinstance(value, numpy.int64) for value in result)


@given(face_with_eyes())
def test_get_eye_deltas(test_face: Face):
    # XXX: There is not much we can test here other than explicit logic
    result = get_eye_deltas(test_face)
    assert len(result) == 2
    assert all(isinstance(value, numpy.int64) for value in result)


@given(face_with_eyes())
def test_get_eye_angle(test_face: Face):
    # XXX: There is not much we can test here other than explicit logic
    result = get_eye_angle(test_face)
    assert isinstance(result, numpy.float64)
    assert result <= 0.0 and result >= -360.0


@given(face_with_eyes())
def test_get_eye_distance(test_face: Face):
    # XXX: There is not much we can test here other than explicit logic
    result = get_eye_distance(test_face)
    assert isinstance(result, numpy.float64)


@settings(deadline=None)
@given(
    image_path(),
    integers(min_value=32, max_value=256),
    floats(min_value=0.1, max_value=0.9),
)
def test_get_normalized_frame(filepath: Path, size: int, offset: float):
    detector = BasicFaceDetector()
    for frame in iter_media_frames(filepath):
        for face in detector.iter_faces(frame):
            result = get_normalized_frame(
                frame,
                face,
                desired_width=size,
                desired_height=size,
                desired_left_eye_position=(offset, offset),
            )

            assert isinstance(result, numpy.ndarray)
            assert result.shape == (size, size, 3)


@given(frame(), face_with_eyes())
def test_get_normalized_frame_uses_defaults(test_frame: Frame, test_face: Face):
    with patch("facelift.helpers.cv2") as mocked_cv2, patch(
        "facelift.helpers.get_eye_distance"
    ) as mocked_get_eye_distance:
        # forcing return value of get_eye_distance to be 1 to avoid randomly getting
        # zero division errors from our random face generation
        mocked_get_eye_distance.return_value = 1
        get_normalized_frame(test_frame, test_face)

        desired_x, desired_y = DEFAULT_NORMALIZED_LEFT_EYE_POSTION
        desired_distance = (
            (1.0 - desired_x) - desired_x
        ) * DEFAULT_NORMALIZED_FACE_SIZE

        mocked_cv2.getRotationMatrix2D(center=ANY, angle=ANY, scale=desired_distance)
        mocked_cv2.warpAffine.assert_called_once_with(
            src=test_frame,
            M=ANY,
            dsize=(DEFAULT_NORMALIZED_FACE_SIZE, DEFAULT_NORMALIZED_FACE_SIZE),
            flags=ANY,
        )
