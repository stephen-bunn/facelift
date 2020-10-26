# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains tests for basic dlib face encoding."""

import math
from pathlib import Path
from typing import List, Optional

import dlib
import numpy
import pytest
from hypothesis import given, settings
from hypothesis.strategies import just, lists, none

from facelift.capture import iter_media_frames
from facelift.detect import BasicFaceDetector, FullFaceDetector
from facelift.encode import BasicFaceEncoder, get_encoder
from facelift.types import Encoder, Encoding, Face

from .strategies import encoding, image_path, pathlib_path, resnet_model_path


@settings(deadline=None)
@given(resnet_model_path())
def test_get_encoder(filepath: Path):
    encoder = get_encoder(filepath)
    assert encoder is not None
    # TODO: this test case is just a shortcut around verifying the Encoder Protocol
    assert isinstance(encoder, dlib.face_recognition_model_v1)


@given(pathlib_path())
def test_get_encoder_raises_FileNotFoundError_when_invalid_filepath_given(
    filepath: Path,
):
    with pytest.raises(FileNotFoundError):
        get_encoder(filepath)


@settings(deadline=None)
@given(image_path())
def test_BasicFaceEncoder_raises_ValueError_with_faces_from_FullFaceDetector(
    media_filepath: Path,
):
    encoder = BasicFaceEncoder()
    detector = FullFaceDetector()
    frame = next(iter_media_frames(media_filepath))
    face = next(detector.iter_faces(frame))
    assert isinstance(face, Face)

    with pytest.raises(ValueError):
        encoder.get_encoding(frame, face)


@settings(deadline=None)
@given(image_path())
def test_BasicFaceEncoder_get_encoding(media_filepath: Path):
    encoder = BasicFaceEncoder()
    detector = BasicFaceDetector()
    frame = next(iter_media_frames(media_filepath))
    face = next(detector.iter_faces(frame))
    assert isinstance(face, Face)

    encoding = encoder.get_encoding(frame, face)
    assert isinstance(encoding, numpy.ndarray)
    assert encoding.shape == (128,)


@given(none(), just([]))
def test_BasicFaceEncoder_get_encoding_returns_infinity_with_no_known_encodings(
    source_encoding: Optional[Encoding], known_encodings: List[Encoding]
):
    encoder = BasicFaceEncoder()
    score = encoder.score_encoding(source_encoding, known_encodings)  # noqa
    assert isinstance(score, float)
    assert score == math.inf


@given(encoding(), lists(encoding(), min_size=1))
def test_BasicFaceEncoder_score_encoding(
    source_encoding: Encoding, known_encodings: List[Encoding]
):
    encoder = BasicFaceEncoder()
    score = encoder.score_encoding(source_encoding, known_encodings)
    print(score)
    assert isinstance(score, float)
    assert score >= 0
