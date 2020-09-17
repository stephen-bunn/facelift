# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains composite strategies related to content testing."""

from glob import glob
from pathlib import Path
from typing import List, Tuple, cast

from hypothesis.strategies import (
    SearchStrategy,
    composite,
    just,
    one_of,
    sampled_from,
    tuples,
)

from facelift.content.types import MediaType

from ..constants import IMAGES_DIRPATH, VIDEOS_DIRPATH
from .constants import SAMPLE_MAGIC


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
def media(draw) -> SearchStrategy[Tuple[Path, MediaType]]:
    """Composite strategy for getting a testing filepath and the desired media type."""

    return draw(
        one_of(
            tuples(image_path(), just(MediaType.IMAGE)),
            tuples(video_path(), just(MediaType.VIDEO)),
        )
    )
