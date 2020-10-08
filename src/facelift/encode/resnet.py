# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""
"""

import abc
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

import dlib
import numpy

from ..constants import DLIB_RESNET_ENCODER_V1_MODEL_NAME, ENCODERS_DIRPATH
from ..types import Face, FaceFeature, Frame

DEFAULT_ENCODING_JITTER = 0
DEFAULT_ENCODING_PADDING = 0.25


@lru_cache()
def get_encoder(model_filepath: Path) -> dlib.face_recognition_model_v1:
    if not model_filepath.is_file():
        raise FileNotFoundError(f"No such file {model_filepath!s} exists")

    return dlib.face_recognition_model_v1(model_filepath.as_posix())


class BaseResnetEncoder(abc.ABC):
    @abc.abstractproperty
    def model_filepath(self) -> Path:
        raise NotImplementedError(
            f"{self.__class__.__qualname__!s} has no associated encoding model"
        )

    def get_encoding(
        self,
        frame: Frame,
        face: Face,
        jitter: int = DEFAULT_ENCODING_JITTER,
        padding: float = DEFAULT_ENCODING_PADDING,
    ) -> numpy.ndarray:
        encoder = get_encoder(self.model_filepath)
        face_chip = dlib.get_face_chip(frame, face.raw)
        return numpy.array(encoder.compute_face_descriptor(face_chip))

    def score_encoding(
        self,
        source_encoding: numpy.ndarray,
        known_encodings: List[numpy.ndarray],
        tolerance: float,
    ) -> float:
        if len(known_encodings) <= 0:
            return 0.0

        return (
            numpy.sum(
                numpy.linalg.norm(
                    x=[encoding for encoding in known_encodings] - source_encoding,
                    axis=1,
                )
                <= tolerance
            )
            / len(known_encodings)
        )


class BasicResnetEncoder(BaseResnetEncoder):

    model_filepath: Path = ENCODERS_DIRPATH.joinpath(DLIB_RESNET_ENCODER_V1_MODEL_NAME)

    def get_encoding(
        self,
        frame: Frame,
        face: Face,
        jitter: int = DEFAULT_ENCODING_JITTER,
        padding: float = DEFAULT_ENCODING_PADDING,
    ) -> numpy.ndarray:
        if FaceFeature.FOREHEAD in face.landmarks:
            raise ValueError(
                f"{self.__class__.__qualname__!r} cannot encode features detected "
                "with the 'FullFaceDetector'"
            )

        return super().get_encoding(frame, face, jitter=jitter, padding=padding)
