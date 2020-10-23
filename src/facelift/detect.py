# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains the available bulitin face detectors.

The included detectors will handle the necessary process for taking a read frame and
discovering all the available faces and included landmarks.
If you have a custom ``face_landmarks`` model, you can inherit from
:class:`~.BaseLandmarkDetector` to detect and return faces using a custom model.

Examples:
    >>> from facelift.detect import BasicFaceDetector
    >>> from facelift.capture import iter_media_frames
    >>> detector = BasicFaceDetector()
    >>> for frame in iter_media_frames(MEDIA_FILEPATH):
    ...     for face in detector.iter_faces(frame):
    ...         print(face)
"""

import abc
from functools import lru_cache
from pathlib import Path
from typing import Dict, Generator, List, Tuple

import dlib
import numpy
from cached_property import cached_property

from .constants import (
    BASIC_FACE_DETECTOR_MODEL_NAME,
    FULL_FACE_DETECTOR_MODEL_NAME,
    LANDMARKS_DIRPATH,
    PARTIAL_FACE_DETECTOR_MODEL_NAME,
)
from .transform import crop
from .types import Detector, Face, FaceFeature, Frame, PointSequence, Predictor


@lru_cache()
def get_predictor(model_filepath: Path) -> Predictor:
    """Build a predictor callable for a given landmark model.

    Args:
        model_filepath (~pathlib.Path):
            The path to the landmark model

    Raises:
        FileNotFoundError: If the given model filepath does not exist

    Returns:
        :attr:`~.types.Predictor`: The new callable to predict face shapes
    """

    if not model_filepath.is_file():
        raise FileNotFoundError(f"No such file {model_filepath!s} exists")

    return dlib.shape_predictor(model_filepath.as_posix())


@lru_cache()
def get_detector() -> Detector:
    """Build the generic detector callable.

    This detector comes directly from the dlib FHOG frontal face detector.

    Returns:
        :attr:`~.types.Detector`: The new callable to detect face bounds
    """

    return dlib.get_frontal_face_detector()


class BaseLandmarkDetector(abc.ABC):
    """An abstract landmark detector class that each landmark model should inherit from.

    Raises:
        NotImplementedError: If the ``model_filepath`` property is not implemented
        NotImplementedError: If the ``landmark_slices`` property is not implemented
    """

    @abc.abstractproperty
    def model_filepath(self) -> Path:  # pragma: no cover
        """Property filepath to the landmarks model that should be used for detection.

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """

        raise NotImplementedError(
            f"{self.__class__.__qualname__!s} has no associated landmark model"
        )

    @abc.abstractproperty
    def landmark_slices(self) -> Dict[FaceFeature, Tuple[int, int]]:  # pragma: no cover
        """Property mapping of facial features to face point slices.

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """

        raise NotImplementedError(
            f"{self.__class__.__qualname__!s} has no defined landmark feature slices"
        )

    @cached_property
    def predictor(self) -> Predictor:
        """Predictor to use in face landmark detection.

        Returns:
            :attr:`~.types.Predictor`: The predictor callable.
        """

        return get_predictor(self.model_filepath)

    @cached_property
    def detector(self) -> Detector:  # pragma: no cover
        """Detector to use in face bounds detection.

        Returns:
            :attr:`~.types.Detector`: The detector callable.
        """

        return get_detector()

    @staticmethod
    def shape_to_points(
        shape: dlib.full_object_detection, dtype: str = "int"
    ) -> PointSequence:
        """Convert dlib shapes to point sequences.

        Example:
            After getting a detected face shape from dlib, we need to convert it back
            into a ``numpy.ndarray`` so OpenCV can use it.

            >>> from facelift.detect import BasicFaceDetector
            >>> detector = BasicFaceDetector()
            >>> for face_bounds in detector.detector(frame, 0):
            ...     face_shape = detector.predictor(frame, face_bounds)
            ...     face_features = detector.shape_to_points(face_shape)

        Args:
            shape (dlib.full_object_detection_):
                The detected dlib shape.
            dtype (str, optional):
                The point type to use when converting the given shape to points.
                Defaults to "int".

        Returns:
            :attr:`~.types.PointSequence`: The newly created sequence of points.
        """

        points = numpy.zeros((shape.num_parts, 2), dtype=dtype)
        for index in range(shape.num_parts):
            points[index] = (shape.part(index).x, shape.part(index).y)

        return points

    @staticmethod
    def slices_to_landmarks(
        points: PointSequence, feature_slices: Dict[FaceFeature, Tuple[int, int]]
    ) -> Dict[FaceFeature, PointSequence]:
        """Group point sequences to features based on point index slices.

        Helper function to automatically group features when given the feature slice
        definition.
        This feature slice definition is a basic way to easily categorize the features
        discovered from the dlib predictor as an actual :class:`~.types.FaceFeature`.

        Examples:
            >>> from facelift.detect import BasicFaceDetector
            >>> detector = BasicFaceDetector()
            >>> for face_bounds in detector.detector(frame, 0):
            ...     face_shape = detector.predictor(frame, face_bounds)
            ...     face_features = detector.shape_to_points(face_shape)
            ...     grouped_features = detector.slices_to_landmarks(face_features)

        Args:
            points (:attr:`~.types.PointSequence`):
                The points to extract feature sequences from.
            feature_slices (Dict[:class:`~.types.FaceFeature`, Tuple[int, int]]):
                A dictionary of :class:`~.types.FaceFeature` and slice tuples.

        Returns:
            Dict[:class:`~.types.FaceFeature`, :attr:`~.types.PointSequence`]:
                The dictionary of features and grouped point sequences.
        """

        return {
            feature: points[slice(*point_slice)]
            for feature, point_slice, in feature_slices.items()
        }

    def get_landmarks(self, points: PointSequence) -> Dict[FaceFeature, PointSequence]:
        """Get the mapping of face features and point sequences for extracted points.

        Args:
            points (:attr:`~.types.PointSequence`):
                The sequence of extracted points from dlib.

        Returns:
            Dict[:class:`~.types.FaceFeature`, :attr:`~.types.PointSequence`]:
                The dictionary of face features and point sequences.
        """

        return self.slices_to_landmarks(points, self.landmark_slices)

    def iter_faces(
        self, frame: Frame, upsample: int = 0
    ) -> Generator[Face, None, None]:
        """Iterate over detected faces within a given :attr:`~.types.Frame`.

        Examples:
            Get detected faces from the first available webcam.

            >>> from facelift.capture import iter_stream_frames
            >>> from facelift.detect import BasicFaceDetector
            >>> detector = BasicFaceDetector()
            >>> for frame in iter_stream_frames():
            ...     for face in detector.iter_faces(frame):
            ...         print(face)

        Args:
            frame (:attr:`~.types.Frame`):
                The frame to detect faces in.
            upsample (int, optional):
                The number of times to scale up the image before detecting faces.
                Defaults to 0.

        Yields:
            :class:`~.types.Face`:
                A detected face within the image, this has no guarantee of order if
                multiple faces are detected
        """

        for face_bounds in self.detector(frame, upsample):
            face_shape = self.predictor(frame, face_bounds)

            yield Face(
                raw=face_shape,
                landmarks=self.get_landmarks(self.shape_to_points(face_shape)),
                frame=crop(
                    frame,
                    (face_bounds.left(), face_bounds.top()),
                    (face_bounds.right(), face_bounds.bottom()),
                ),
            )


class BasicFaceDetector(BaseLandmarkDetector):
    """Basic face detector.

    This face detector gives single point positions for the outside of both eyes and the
    philtrum (right beneath the nose).
    For rendering, these facial features must be rendered as points rather than lines.

    This model is useful for just finding faces and getting normalized face frames.
    This model is not useful for emotion, perspective, or face state detection.
    """

    model_filepath: Path = LANDMARKS_DIRPATH.joinpath(BASIC_FACE_DETECTOR_MODEL_NAME)
    landmark_slices: Dict[FaceFeature, Tuple[int, int]] = {
        FaceFeature.LEFT_EYE: (0, 1),
        FaceFeature.RIGHT_EYE: (2, 3),
        FaceFeature.NOSE: (4, 5),
    }


class PartialFaceDetector(BaseLandmarkDetector):
    """Partial face detector.

    This face detector detects all features of a face except for the forehead.
    This model is useful for most any purpose.
    However, if all you are doing is detecting faces, you should probably use the
    :class:`~.BasicFaceDetector` instead.
    """

    model_filepath: Path = LANDMARKS_DIRPATH.joinpath(PARTIAL_FACE_DETECTOR_MODEL_NAME)
    landmark_slices: Dict[FaceFeature, Tuple[int, int]] = {
        FaceFeature.JAW: (0, 17),
        FaceFeature.RIGHT_EYEBROW: (17, 22),
        FaceFeature.LEFT_EYEBROW: (22, 27),
        FaceFeature.NOSE: (27, 36),
        FaceFeature.RIGHT_EYE: (36, 42),
        FaceFeature.LEFT_EYE: (42, 48),
        FaceFeature.MOUTH: (48, 60),
        FaceFeature.INNER_MOUTH: (60, 68),
    }


class FullFaceDetector(BaseLandmarkDetector):
    """Full face detector.

    This face detector detects all available frontal face features.
    This model can be used for most anything, but may not be the most efficient.
    If you are just trying to detect faces, you should probably use the
    :class:`~.BasicFaceDetector` instead.
    """

    model_filepath: Path = LANDMARKS_DIRPATH.joinpath(FULL_FACE_DETECTOR_MODEL_NAME)
    landmark_slices: Dict[FaceFeature, Tuple[int, int]] = {
        FaceFeature.JAW: (0, 17),
        FaceFeature.RIGHT_EYEBROW: (17, 22),
        FaceFeature.LEFT_EYEBROW: (22, 27),
        FaceFeature.NOSE: (27, 36),
        FaceFeature.RIGHT_EYE: (36, 42),
        FaceFeature.LEFT_EYE: (42, 48),
        FaceFeature.MOUTH: (48, 68),
        FaceFeature.INNER_MOUTH: (60, 68),
        FaceFeature.FOREHEAD: (69, 81),
    }
    _forehead_index_sequence: List[int] = [8, 6, 7, 0, 1, 2, 11, 3, 4, 10, 5, 9]

    def get_landmarks(self, points: PointSequence) -> Dict[FaceFeature, PointSequence]:
        """Get the mapping of face features and point sequences for extracted points.

        Args:
            points (:attr:`~.types.PointSequence`):
                The sequence of extracted points from dlib.

        Returns:
            Dict[:class:`~.types.FaceFeature`, :attr:`~.types.PointSequence`]:
                The dictionary of face features and point sequences.
        """

        landmarks = {}
        for feature, point_slice in self.landmark_slices.items():
            if feature == FaceFeature.FOREHEAD:
                # NOTE: The 81 point face landmark model has improper ordering for the
                # forehead feature. This is us correcting the point ordering for
                # better classification and rendering
                forehead_points = points[slice(*point_slice)]
                landmarks[FaceFeature.FOREHEAD] = numpy.array(
                    [forehead_points[index] for index in self._forehead_index_sequence]
                )
            else:
                landmarks[feature] = points[slice(*point_slice)]

        return landmarks
