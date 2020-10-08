# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains module-wide constants.

Attributes:
    DATA_DIRPATH (Path):
        The absolute path to the module's included data directory.
    LANDMARKS_DIRPATH (Path):
        The absolute path to the module's included landmarks model directory.
    BASIC_FACE_DETECTOR_MODEL_NAME (str):
        The name of the basic 5 feature landmark model
    PARTIAL_FACE_DETECTOR_MODEL_NAME (str):
        The name of the partial 68 feature landmark model
    FULL_FACE_DETECTOR_MODEL_NAME (str):
        The name of the full 81 feature landmark model
"""

from pathlib import Path

DATA_DIRPATH = Path(__file__).parent.joinpath("data").absolute()
LANDMARKS_DIRPATH = DATA_DIRPATH.joinpath("landmarks")
ENCODERS_DIRPATH = DATA_DIRPATH.joinpath("encoders")

BASIC_FACE_DETECTOR_MODEL_NAME = "shape_predictor_5_face_landmarks.dat"
PARTIAL_FACE_DETECTOR_MODEL_NAME = "shape_predictor_68_face_landmarks.dat"
FULL_FACE_DETECTOR_MODEL_NAME = "shape_predictor_81_face_landmarks.dat"

DLIB_RESNET_ENCODER_V1_MODEL_NAME = "dlib_face_recognition_resnet_model_v1.dat"
