# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains mechanisms to extract details or normalized details for detected faces."""

from typing import Optional, Tuple

import cv2
import numpy

from ..types import Face, FaceFeature, Frame

DEFAULT_NORMALIZED_FACE_SIZE = 256
DEFAULT_NORMALIZED_LEFT_EYE_POSTION = (0.35, 0.35)


def get_eye_positions(face: Face) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """Get the center position tuples of eyes from the given face.

    Args:
        face (Face): The face to extract eye positions from

    Raises:
        ValueError: If the given face is missing either left or right eye landmarks

    Returns:
        Tuple[Tuple[int, int], Tuple[int, int]]:
            A tuple of (left eye position, right eye position)
    """

    left_eye = face.landmarks.get(FaceFeature.LEFT_EYE)
    right_eye = face.landmarks.get(FaceFeature.RIGHT_EYE)

    if not left_eye or not right_eye:
        raise ValueError(f"Face {face!r} doesn't have required eye landmarks")

    return (
        left_eye.mean(axis=0).astype("int"),  # type: ignore
        right_eye.mean(axis=0).astype("int"),  # type: ignore
    )


def get_eye_center_position(face: Face) -> Tuple[int, int]:
    """Get the center position between the eyes of the given face.

    Args:
        face (Face): The face to extract the center position from

    Returns:
        Tuple[int, int]: The position directly between the eyes of the face
    """

    (left_start, left_end), (right_start, right_end) = get_eye_positions(face)
    return (left_start + right_start) // 2, (left_end + right_end) // 2


def get_eye_deltas(face: Face) -> Tuple[int, int]:
    """Get the difference between eye positions of the given face.

    Args:
        face (Face): The face to get the eye deltas from

    Returns:
        Tuple[int, int]: A tuple of (x delta, y delta) for the given face's eyes
    """

    (left_start, left_end), (right_start, right_end) = get_eye_positions(face)
    return ((right_start - left_start), (right_end - left_end))


def get_eye_angle(face: Face) -> numpy.ndarray:
    """Get the angle the eyes are currently at for the given face.

    Args:
        face (Face): The face to get the eye angle from

    Returns:
        numpy.ndarray:
            A matrix describing the current angle of the eyes in the face.
    """

    delta_x, delta_y = get_eye_deltas(face)
    return numpy.degrees(numpy.arctan2(delta_y, delta_x)) - 180


def get_eye_distance(face: Face) -> numpy.ndarray:
    """Get the distance between the eyes of the given face.

    Args:
        face (Face): The face to get the eye distance from

    Returns:
        numpy.ndarray:
            A matrix describing the difference between the face's eye landmarks.
    """

    delta_x, delta_y = get_eye_deltas(face)
    return numpy.sqrt((delta_x ** 2) + (delta_y ** 2))


def get_normalized_frame(
    frame: Frame,
    face: Face,
    desired_width: Optional[int] = None,
    desired_height: Optional[int] = None,
    desired_left_eye_position: Optional[Tuple[float, float]] = None,
) -> Frame:
    """Get a normalized face frame where the face is aligned, cropped, and positioned.

    Args:
        frame (Frame): The original frame the face was detected from
        face (Face): The detected face to use when extracting a normalized face frame
        desired_width (Optional[int], optional):
            The desired width of the normalized frame. Defaults to None.
        desired_height (Optional[int], optional):
            The desired height of the normalized frame. Defaults to None.
        desired_left_eye_position (Optional[Tuple[float, float]], optional):
        The desired position point for the left eye (this position is a value between
            0.0 and 1.0 indicating the percentage of the frame). Defaults to None.

    Returns:
        Frame: The normalized face frame.
    """

    if not desired_width:
        desired_width = DEFAULT_NORMALIZED_FACE_SIZE
    if not desired_height:
        desired_height = DEFAULT_NORMALIZED_FACE_SIZE
    if not desired_left_eye_position:
        desired_left_eye_position = DEFAULT_NORMALIZED_LEFT_EYE_POSTION

    desired_x, desired_y = desired_left_eye_position
    desired_distance = ((1.0 - desired_x) - desired_x) * desired_width

    eye_center = get_eye_center_position(face)
    rotation_matrix = cv2.getRotationMatrix2D(
        center=eye_center,
        angle=get_eye_angle(face),
        scale=desired_distance / get_eye_distance(face),
    )

    left_center, right_center = eye_center
    rotation_matrix[0, 2] += (desired_width * 0.5) - left_center
    rotation_matrix[1, 2] += (desired_height * desired_y) - right_center

    return cv2.warpAffine(
        src=frame,
        M=rotation_matrix,
        dsize=(desired_width, desired_height),
        flags=cv2.INTER_CUBIC,
    )
