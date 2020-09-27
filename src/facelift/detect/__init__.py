# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains mechanisms for detecting and extracting faces from frames."""

from .landmark import (
    BaseLandmarkDetector,
    BasicFaceDetector,
    FullFaceDetector,
    PartialFaceDetector,
)

__all__ = [
    "BaseLandmarkDetector",
    "BasicFaceDetector",
    "FullFaceDetector",
    "PartialFaceDetector",
]
