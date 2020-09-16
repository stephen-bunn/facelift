# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains composite strategies related to content testing."""

from typing import List, Tuple, cast

from hypothesis.strategies import composite, sampled_from

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
