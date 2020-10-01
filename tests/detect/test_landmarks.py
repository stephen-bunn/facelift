# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains tests for basic dlib facial feature landmark detection."""

from pathlib import Path
from typing import Dict, List, Tuple

import dlib
import numpy
import pytest
from hypothesis import given, settings
from hypothesis.strategies import dictionaries, just

from facelift.constants import (
    BASIC_FACE_DETECTOR_MODEL_NAME,
    FULL_FACE_DETECTOR_MODEL_NAME,
    PARTIAL_FACE_DETECTOR_MODEL_NAME,
)
from facelift.content.capture import iter_media_frames
from facelift.detect.landmark import (
    BaseLandmarkDetector,
    BasicFaceDetector,
    FullFaceDetector,
    PartialFaceDetector,
    get_detector,
    get_predictor,
)
from facelift.types import Face, FaceFeature

from ..strategies import (
    face_feature,
    face_shape,
    image_path,
    landmark_model_path,
    pathlib_path,
    video_path,
)


@settings(deadline=None)
@given(landmark_model_path())
def test_get_predictor(filepath: Path):
    # we need to disable the deadline for this test as some of the models exceed 90MB
    # which takes a while to load and cache
    assert isinstance(get_predictor(filepath), dlib.shape_predictor)


@given(pathlib_path())
def test_get_predictor_raises_FileNotFoundError_when_invalid_filepath_given(
    filepath: Path,
):
    with pytest.raises(FileNotFoundError):
        get_predictor(filepath)


def test_get_detector():
    assert isinstance(get_detector(), dlib.fhog_object_detector)


def test_BaseLandmarkDetector_raises_TypeError_since_it_is_abstract():
    with pytest.raises(TypeError):
        BaseLandmarkDetector()


@given(face_shape())
def test_BaseLandmarkDetector_shape_to_points(face_shape: dlib.full_object_detection):
    result = BaseLandmarkDetector.shape_to_points(face_shape)
    assert isinstance(result, numpy.ndarray)
    assert result.shape == (face_shape.num_parts, 2)


@given(
    just([(0, 0), (1, 1)]),
    dictionaries(face_feature(), just((0, 2)), min_size=1),
)
def test_BaseLandmarkDetector_slices_to_landmarks(
    points: List[Tuple[int, int]], slices: Dict[FaceFeature, Tuple[int, int]]
):
    # NOTE: this test is fairly weak as we are just ensuring that the call returns the
    # right structure of data rather than testing all possible edge-cases
    results = BaseLandmarkDetector.slices_to_landmarks(points, slices)
    assert len(results) == len(slices)
    assert all(points == [(0, 0), (1, 1)] for points in results.values())


def test_BasicFaceDetector_predictor():
    detector = BasicFaceDetector()
    assert detector.model_filepath.name == BASIC_FACE_DETECTOR_MODEL_NAME
    assert isinstance(detector.predictor, dlib.shape_predictor)


@settings(deadline=None)
@given(video_path())
def test_BasicFaceDetector_iter_faces(media_filepath: Path):
    detector = BasicFaceDetector()
    for frame in iter_media_frames(media_filepath):
        for face in detector.iter_faces(frame):
            assert isinstance(face, Face)


@settings(deadline=None)
@given(image_path())
def test_BasicFaceDetector_iter_faces_landmarks(media_filepath: Path):
    detector = BasicFaceDetector()
    face = next(detector.iter_faces(next(iter_media_frames(media_filepath))))
    assert isinstance(face, Face)
    assert all(
        feature in face.landmarks
        for feature in [FaceFeature.LEFT_EYE, FaceFeature.RIGHT_EYE, FaceFeature.NOSE]
    )


def test_PartialFaceDetector_predictor():
    detector = PartialFaceDetector()
    assert detector.model_filepath.name == PARTIAL_FACE_DETECTOR_MODEL_NAME
    assert isinstance(detector.predictor, dlib.shape_predictor)


@settings(deadline=None)
@given(image_path())
def test_PartialFaceDetector_iter_faces_landmarks(media_filepath: Path):
    detector = PartialFaceDetector()
    face = next(detector.iter_faces(next(iter_media_frames(media_filepath))))
    assert isinstance(face, Face)
    assert all(
        feature in face.landmarks
        for feature in [
            FaceFeature.LEFT_EYE,
            FaceFeature.RIGHT_EYE,
            FaceFeature.NOSE,
            FaceFeature.LEFT_EYEBROW,
            FaceFeature.RIGHT_EYEBROW,
            FaceFeature.MOUTH,
            FaceFeature.INNER_MOUTH,
            FaceFeature.JAW,
        ]
    )


def test_FullFaceDetector_predictor():
    detector = FullFaceDetector()
    assert detector.model_filepath.name == FULL_FACE_DETECTOR_MODEL_NAME
    assert isinstance(detector.predictor, dlib.shape_predictor)


@settings(deadline=None)
@given(image_path())
def test_FullFaceDetector_iter_faces_landmarks(media_filepath: Path):
    detector = FullFaceDetector()
    face = next(detector.iter_faces(next(iter_media_frames(media_filepath))))
    assert isinstance(face, Face)
    assert all(
        feature in face.landmarks
        for feature in [
            FaceFeature.LEFT_EYE,
            FaceFeature.RIGHT_EYE,
            FaceFeature.NOSE,
            FaceFeature.LEFT_EYEBROW,
            FaceFeature.RIGHT_EYEBROW,
            FaceFeature.MOUTH,
            FaceFeature.INNER_MOUTH,
            FaceFeature.JAW,
            FaceFeature.FOREHEAD,
        ]
    )
