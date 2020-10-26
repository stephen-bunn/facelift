# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains module-wide used types.

.. _dlib.rectangle:
    http://dlib.net/python/index.html#dlib.rectangle
.. _dlib.full_object_detection:
    http://dlib.net/python/index.html#dlib.full_object_detection

Attributes:
    Frame (``NDArray[(Any, Any, 3), UInt8]``):
        An aliased type for a basic numpy array that gets given to use via OpenCV.
    Point (``NDArray[(2,), Int32]``):
        A single x, y coordinate that describes a single positional point.
    PointSequence (``NDArray[(Any, 2), Int32]``):
        A sequence of points that is typically used to describe a face feature or a line
        during rendering.
    Encoding (``NDArray[(128,), Int32]``):
        A 128 dimension encoding of a detected face for a given frame.

    Detector (Callable[[:attr:`~Frame`, :class:`int`], :attr:`~PointSequence`]):
        Callable that takes a frame and an upsample count and discovers the bounds of
        a face within the frame.
    Predictor (Callable[[:attr:`~Frame`, dlib.rectangle_], dlib.full_object_detection_])
        Callable which takes a frame and detected face bounds to discover the shape and
        features within the face.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, List, Tuple, Type

import dlib
import numpy
from typing_extensions import (  # NOTE: extensions not required with Python >=3.9
    Protocol,
)

# XXX: Numpy does not currently support typing, so we are forced to hack around this for
# now. There are several other projects that are WIP to provide some typing around
# Numpy arrays (such as nptyping). Unfortunately, these typing libraries were not
# designed with static type checking in mind so we cannot use them as we need to here.
# (https://github.com/ramonhagenaars/nptyping/issues/34)

Frame = Type[numpy.ndarray]  # FIXME: this type is NDArray[(Any, Any, 3), UInt8]
Point = Tuple[int, int]  # FIXME: this type is NDArray[(2,), Int]
PointSequence = List[Point]  # FIXME: this type is NDArray[(Any, 2), Int]
Encoding = Type[numpy.ndarray]  # FIXME: this type is NDArray[(128,), Int]

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


# Type manually derived from `dlib.face_recognition_model_v1` for mypy's sake
# http://dlib.net/python/index.html#dlib.face_recognition_model_v1
class Encoder(Protocol):
    """Protocol class for ``dlib.face_recognition_model_v1.``."""

    def compute_face_descriptor(
        self,
        frame: Frame,
        face: dlib.full_object_detection,
        num_jitters: int = 0,
        padding: float = 0.25,
    ) -> dlib.vector:  # pragma: no cover
        """Compute a descriptor for a detected face frame.

        Args:
            frame (:attr:`~.types.Frame`):
                The frame containing just the detected face.
            face (:class:`dlib.full_object_detection`):
                The raw detected face bounds within the given face frame.
            num_jitters (int):
                The number of jitters to run through the dector projection.
                Defaults to 0.
            padding (float):
                The default padding around the face.
                Defaults to 0.25.

        Returns:
            dlib.vector:
                The face descriptor (encoding).
        """

        ...


class MediaType(Enum):
    """Enumeration of acceptable media types for processing.

    Attributes:
        IMAGE:
            Defines media that contains just a single frame to process.
        VIDEO:
            Defines media that contains a known number of frames to process.
        STREAM:
            Defines media that contains an unknown number of frames to process.
    """

    IMAGE = "image"
    VIDEO = "video"
    STREAM = "stream"


class FaceFeature(Enum):
    """Enumeration of features of a face that we can detect.

    Attributes:
        NOSE:
            The nose of a face.
        JAW:
            The jaw line of a face.
        MOUTH:
            The external bounds of the mouth of a face.
        INNER_MOUTH:
            The internal bounds of the mouth of a face.
        RIGHT_EYE:
            The external and internal bounds of the right eye of a face.
        LEFT_EYE:
            The external and internal bounds of the left eye of a face.
        RIGHT_EYEBROW:
            The right eyebrow of a face.
        LEFT_EYEBROW:
            The left eyebrow of a face.
        FOREHEAD:
            The forehead curvature of a face.
    """

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

    Args:
        raw (:class:`dlib.full_object_detection`):
            The raw ``dlib`` object detection container.
        landmarks (Dict[:class:`~FaceFeature`, :attr:`~PointSequence`]):
            Mapping of extracted face features to the sequence of points describing
            those features.
        frame (:class:`~Frame`):
            The base non-normalized cropped frame of just the face.
    """

    raw: dlib.full_object_detection
    landmarks: Dict[FaceFeature, PointSequence]
    frame: Frame

    @property
    def rectangle(self) -> PointSequence:
        """Point sequence representation of the detected face's bounds.

        This property is useful for properly positioning text around the detected face
        as the :func:`~.render.draw_text` needs a text container to be defined.

        Returns:
            :attr:`~.types.PointSequence`:
                A sequence of 2 points indicating the top-left and bottom-right corners
                of the detected face's bounds.
        """

        start = self.raw.rect.tl_corner()
        end = self.raw.rect.br_corner()

        return numpy.asarray([[start.x, start.y], [end.x, end.y]])
