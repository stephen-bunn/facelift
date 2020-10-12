# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains generic composite strategies for package tests."""

import sys
from pathlib import Path
from string import printable
from typing import Any, Dict, List, Optional, Tuple, Type, cast

import dlib
import numpy
from hypothesis.extra.numpy import arrays as numpy_arrays
from hypothesis.strategies import (
    SearchStrategy,
    binary,
    booleans,
    builds,
    complex_numbers,
    composite,
    dictionaries,
    floats,
    integers,
    just,
    lists,
    none,
    one_of,
    sampled_from,
    text,
    tuples,
)

from facelift.constants import (
    BASIC_FACE_DETECTOR_MODEL_NAME,
    FULL_FACE_DETECTOR_MODEL_NAME,
    LANDMARKS_DIRPATH,
    PARTIAL_FACE_DETECTOR_MODEL_NAME,
)
from facelift.types import Face, FaceFeature, Frame, MediaType, Point, PointSequence

from .buffers import SAMPLE_MAGIC
from .constants import IMAGES_DIRPATH, VIDEOS_DIRPATH


@composite
def builtin_types(
    draw, include: Optional[List[Type]] = None, exclude: Optional[List[Type]] = None
) -> Any:
    """Composite strategy for building an instance of a builtin type.

    This strategy allows you to check against builtin types for when you need to do
    variable validation (which should be rare). By default this composite will generate
    all available types of builtins, however you can either tell it to only generate
    some types or exclude some types. You do this using the ``include`` and ``exclude``
    parameters.

    For example using the ``include`` parameter like the following will ONLY generate
    strings and floats for the samples:

    >>> @given(builtin_types(include=[str, float]))
    ... def test_only_strings_and_floats(value: Union[str, float]):
    ...     assert isinstance(value, (str, float))

    Similarly, you can specify to NOT generate Nones and complex numbers like the
    following example:

    >>> @given(builtin_types(exclude=[None, complex]))
    ... def test_not_none_or_complex(value: Any):
    ...     assert value and not isinstance(value, complex)
    """

    strategies: Dict[Any, SearchStrategy[Any]] = {
        None: none(),
        int: integers(),
        bool: booleans(),
        float: floats(allow_nan=False),
        tuple: builds(tuple),
        list: builds(list),
        set: builds(set),
        frozenset: builds(frozenset),
        str: text(),
        bytes: binary(),
        complex: complex_numbers(),
    }

    to_use = set(strategies.keys())
    if include and len(include) > 0:
        to_use = set(include)

    if exclude and len(exclude) > 0:
        to_use = to_use - set(exclude)

    return draw(
        one_of([strategy for key, strategy in strategies.items() if key in to_use])
    )


@composite
def pathlib_path(draw) -> SearchStrategy[Path]:
    """Composite strategy for buliding a random :class:`~pathlib.Path` instance."""

    return draw(
        just(Path(*draw(lists(text(alphabet=printable, min_size=1), min_size=1))))
    )


@composite
def media_details(draw) -> Tuple[str, str, List[str], bytes]:
    """Composite strategy for building the details to produce a sample media file.

    Examples:
        Sample usage of this composite strategy might look something like this:

        >>> @given(video_details())
        ... def test_video_file(file_details):
        ...     file_format, mimetypes, buffer = file_details
        ...     assert file_format == "mp4"
        ...     assert "video/mp4" in mimetypes
    """

    media_name: str = draw(sampled_from(list(SAMPLE_MAGIC.keys())))
    media_type = cast(str, SAMPLE_MAGIC[media_name]["type"])
    mimetypes = cast(List[str], SAMPLE_MAGIC[media_name]["mimetypes"])
    buffer = cast(bytes, SAMPLE_MAGIC[media_name]["buffer"])

    return (media_name, media_type, mimetypes, buffer)


@composite
def image_path(draw) -> SearchStrategy[Path]:
    """Composite strategy for getting a testing image path."""

    return draw(just(Path(draw(sampled_from(list(IMAGES_DIRPATH.iterdir()))))))


@composite
def video_path(draw) -> SearchStrategy[Path]:
    """Composite strategy for getting a testing video path."""

    return draw(just(Path(draw(sampled_from(list(VIDEOS_DIRPATH.iterdir()))))))


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
def media(draw) -> SearchStrategy[Tuple[Path, MediaType]]:
    """Composite strategy for getting a testing filepath and the desired media type."""

    return draw(
        one_of(
            tuples(image_path(), just(MediaType.IMAGE)),
            tuples(video_path(), just(MediaType.VIDEO)),
        )
    )


@composite
def point(draw) -> SearchStrategy[Point]:
    """Composite strategy to generate a single Point type."""

    return draw(numpy_arrays(numpy.uint32, 2))


@composite
def point_sequence(
    draw, min_size: int = 1, max_size: int = 32
) -> SearchStrategy[PointSequence]:
    """Composite strategy to generate a PointSequence type.

    Args:
        min_size (int):
            The minimum number of points to put in the sequence.
            Defaults to 1.
        max_size (int):
            The maximum number of points to put in the sequence.
            Defaults to 32.

    Returns:
        SearchStrategy[PointSequence]:
            A sequence of points.
    """

    return draw(
        numpy_arrays(
            numpy.uint32, (draw(integers(min_value=min_size, max_value=max_size)), 2)
        )
    )


@composite
def frame(
    draw,
    width_strategy: Optional[SearchStrategy[int]] = None,
    height_strategy: Optional[SearchStrategy[int]] = None,
) -> SearchStrategy[Frame]:
    """Composite strategy for building a random frame as produced by opencv."""

    return draw(
        numpy_arrays(
            numpy.uint8,
            (
                draw(
                    height_strategy
                    if height_strategy
                    else integers(min_value=1, max_value=512)
                ),
                draw(
                    width_strategy
                    if width_strategy
                    else integers(min_value=1, max_value=512)
                ),
                3,
            ),
        )
    )


@composite
def face_feature(draw) -> SearchStrategy[FaceFeature]:
    """Composite strategy for getting a random :class:`~facelift.types.FaceFeature`."""

    return draw(sampled_from(list(FaceFeature)))


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


@composite
def face(
    draw,
    raw_strategy: Optional[SearchStrategy[dlib.full_object_detection]] = None,
    frame_strategy: Optional[SearchStrategy[Frame]] = None,
    landmarks_strategy: Optional[
        SearchStrategy[Dict[FaceFeature, PointSequence]]
    ] = None,
) -> SearchStrategy[Face]:
    """Composite strategy to generate a random face type.

    It is important to note that this strategy will just generate the random types of
    data necessary to produce a :class:`~.types.Face` instance. There is no gurantee that
    this data makes sense in terms of the face existing or the points being in
    appropriate order of the appropriate number.

    For tests dependent on actual faces existing, please actually detect the face using
    supplied testing assets through the :func:`image_path` or :func:`video_path`
    composite strategies.
    """

    return draw(
        just(
            Face(
                raw=draw(raw_strategy if raw_strategy else face_shape()),
                frame=draw(frame_strategy if frame_strategy else frame()),
                landmarks=draw(
                    landmarks_strategy
                    if landmarks_strategy
                    else dictionaries(
                        face_feature(),
                        point_sequence(),
                        min_size=1,
                    )
                ),
            )
        )
    )
