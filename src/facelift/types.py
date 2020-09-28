# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains module-wide used types.

Attributes:
    Frame (nptyping.NDArray[(Any, Any, 3), nptyping.UInt8]): An aliased type for a basic
        numpy array that gets given to use via opencv.
    Point (nptyping.NDArray[(2,), nptyping.Int]): A single x, y coordinate that
        describes a single positional point.
    PointSequence (nptyping.NDArray(Any, 2), nptyping.Int): A sequence of points that
        is typically used to describe a face feature or a line during rendering.

    Detector (Callable[[Frame, int], PointSequence]):
        Callable that takes a frame and an upsample count and discovers the bounds of
        a face within the frame.
    Predictor (Callable[[Frame, dlib.rectangle], dlib.full_object_detection]):
        Callable which takes a frame and detected face bounds to discover the shape and
        features within the face.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, List, Tuple, Type

import dlib
import numpy

# XXX: Numpy does not currently support typing, so we are forced to hack around this for
# now. There are several other projects that are WIP to provide some typing around
# Numpy arrays (such as nptyping). Unfortunately, these typing libraries were not
# designed with static type checking in mind so we cannot use them as we need to here.
# (https://github.com/ramonhagenaars/nptyping/issues/34)

Frame = Type[numpy.ndarray]  # FIXME: this type is NDArray[(Any, Any, 3), UInt8]
Point = Tuple[int, int]  # FIXME: this type is NDArray[(2,), Int]
PointSequence = List[Point]  # FIXME: this type is NDArray[(Any, 2), Int]

# Type manually derived from `dlib.fhog_object_detector` for mypy's sake
# http://dlib.net/python/index.html#dlib.fhog_object_detector
# signature is equivalent to the following:
# (frame: numpy.ndarray, upsample_num_times: int = 0L) -> List[numpy.ndarray]
Detector = Callable[[Frame, int], PointSequence]

# Type manually derived from `dlib.shape_predictor` for mypy's sake
# http://dlib.net/python/index.html#dlib.shape_predictor
# signature is equivalent to the following:
# (frame: numpy.ndarray, face_bound_shape: dlib.rectangle) -> dlib.full_object_detection
# `face_bound_shape` comes directly from a dlib object detector
Predictor = Callable[[Frame, dlib.rectangle], dlib.full_object_detection]


class MediaType(Enum):
    """Defines the acceptable media types for processing.

    Attributes:
        IMAGE (MediaType): Defines media that contains a single frame to process
        VIDEO (MediaType): Defines media that contains a known number of frames to
            process that is more than more than 1
        STREAM (MediaType): Defines media that contains an unknown number of frames to
            process
    """

    IMAGE = "image"
    VIDEO = "video"
    STREAM = "stream"


class FaceFeature(Enum):
    """Enumeration of features of a face that we can detect."""

    NOSE = "nose"
    JAW = "jaw"
    MOUTH = "mouth"
    INNER_MOUTH = "inner_mouth"
    RIGHT_EYE = "right_eye"
    LEFT_EYE = "left_eye"
    RIGHT_EYEBROW = "right_eyebrow"
    LEFT_EYEBROW = "left_eyebrow"
    FOREHEAD = "forehead"


@dataclass
class Face:
    """Describes a detected face.

    Attributes:
        landmarks (Dict[FaceFeature, PointSequence]): Mapping of extracted face features
            to the sequence of points describing those features.
        frame (Frame): The base non-normalized cropped frame of just the face.
    """

    landmarks: Dict[FaceFeature, PointSequence]
    frame: Frame
