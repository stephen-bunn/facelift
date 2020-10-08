# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Facelift.

A simple wrapper for face detection and recognition.
Basic usage looks something like this:

>>> from facelift import iter_media_frames, PartialFaceDetector
>>> detector = PartialFaceDetector()
>>> for frame in iter_media_frames(MEDIA_FILEPATH):
...     for face in detector.iter_faces(frame):
...         # Do something with the face
"""

from .content import iter_media_frames, iter_stream_frames
from .detect import BasicFaceDetector, FullFaceDetector, PartialFaceDetector
from .encode import BasicResnetEncoder

__all__ = [
    "iter_media_frames",
    "iter_stream_frames",
    "BasicFaceDetector",
    "FullFaceDetector",
    "PartialFaceDetector",
    "BasicResnetEncoder",
]
