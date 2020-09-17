# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains content specific types and enums used through the content package.

Attributes:
    Frame (Type[numpy.ndarray]): An aliased type for a basic numpy array that gets given
        to use via opencv.
"""

from enum import Enum
from typing import Type

import numpy

Frame = Type[numpy.ndarray]


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
