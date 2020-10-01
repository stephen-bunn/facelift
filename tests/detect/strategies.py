# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""
"""

import sys
from pathlib import Path
from typing import List, Optional, Tuple

import dlib
from hypothesis.strategies import (
    SearchStrategy,
    composite,
    integers,
    just,
    lists,
    sampled_from,
    tuples,
)

from facelift.constants import (
    BASIC_FACE_DETECTOR_MODEL_NAME,
    FULL_FACE_DETECTOR_MODEL_NAME,
    LANDMARKS_DIRPATH,
    PARTIAL_FACE_DETECTOR_MODEL_NAME,
)


@composite
def landmark_model_path(draw) -> SearchStrategy[Path]:
    """Composite strategy for getting an included landmark model path."""

    return draw(
        just(
            LANDMARKS_DIRPATH.joinpath(
                draw(
                    sampled_from(
                        [
                            BASIC_FACE_DETECTOR_MODEL_NAME,
                            PARTIAL_FACE_DETECTOR_MODEL_NAME,
                            FULL_FACE_DETECTOR_MODEL_NAME,
                        ]
                    )
                )
            )
        )
    )


@composite
def face_shape(draw) -> SearchStrategy[dlib.full_object_detection]:
    """Composite strategy to build a completely random dlib detected feature."""

    top_left = draw(
        tuples(
            integers(min_value=0, max_value=sys.maxsize - 1),
            integers(min_value=0, max_value=sys.maxsize - 1),
        )
    )
    bottom_right = draw(
        tuples(
            integers(min_value=top_left[0] + 1, max_value=sys.maxsize),
            integers(min_value=top_left[-1] + 1, max_value=sys.maxsize),
        ),
    )

    rectangle = dlib.rectangle(*top_left, *bottom_right)
    points = draw(
        lists(
            just(
                dlib.point(
                    draw(integers(min_value=top_left[0], max_value=bottom_right[0])),
                    draw(integers(min_value=top_left[-1], max_value=bottom_right[-1])),
                )
            ),
            min_size=1,
            unique=True,
        )
    )
    return draw(just(dlib.full_object_detection(rectangle, points)))
