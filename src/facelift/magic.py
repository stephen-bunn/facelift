# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

"""Contains helpers and enums used to guess the type of media that is being processed.

This module utilizes `python-magic <https://github.com/ahupp/python-magic>`_ which
in turn uses `libmagic <https://linux.die.net/man/3/libmagic>`_ to guess the appropriate
mimetype of some byte buffer.

Attributes:
    DEFAULT_MAGIC_BUFFER_SIZE (int): The default number of bytes to try and read from
        when making a guess at the mimetype of some file.
"""

from pathlib import Path
from typing import Optional

from .types import MediaType

try:
    import magic
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "libmagic binary not found, please install all necessary system requirements "
        "documented at https://bit.ly/3hJ6IGI"
    ) from exc


DEFAULT_MAGIC_BUFFER_SIZE = 2 ** 11


def get_mimetype(
    media_filepath: Path, buffer_size: Optional[int] = None
) -> Optional[str]:
    """Try and determine the mimetype for content at the given filepath.

    Args:
        media_filepath (~pathlib.Path):
            The filepath to guess the mimetype of
        buffer_size (Optional[int], optional):
            The number of bytes to use for guessing the mimetype of the given file.
            Defaults to the value of :attr:`~DEFAULT_MAGIC_BUFFER_SIZE`.

    Raises:
        FileNotFoundError: When the provided filepath does not exist

    Returns:
        Optional[str]: The guessed mimetype if a guess can be safely made
    """

    if not media_filepath.is_file():
        raise FileNotFoundError(f"no such file {media_filepath!s} exists")

    with media_filepath.open("rb") as media_buffer:
        return magic.from_buffer(
            media_buffer.read(buffer_size or DEFAULT_MAGIC_BUFFER_SIZE), mime=True
        )


def get_media_type(
    media_filepath: Path, buffer_size: Optional[int] = None, validate: bool = False
) -> Optional[MediaType]:
    """Try and determine the media type for content at the given filepath.

    Args:
        media_filepath (~pathlib.Path):
            The filepath to guess the media type of
        buffer_size (Optional[int], optional):
            The number of bytes to use for guessing the media type of the given file.
            Defaults to the value of :attr:`~DEFAULT_MAGIC_BUFFER_SIZE`.
        validate (bool, optional):
            If truthy, a :class:`ValueError` will be raised if the given file's mimetype
            does not match a supported :class:`~.types.MediaType`.
            Defaults to False.

    Raises:
        FileNotFoundError:
            When the provided filepath does not exist
        ValueError:
            When ``validate`` is truthy and the given filepath does not match a
            supported :class:`~.types.MediaType`

    Returns:
        Optional[~.types.MediaType]:
            The appropriate media type enum attribute for the given filepath,
            if a successful guess and media type match is made
    """

    mimetype = get_mimetype(media_filepath, buffer_size=buffer_size)
    if not mimetype:
        return None

    mime_prefix, *_ = mimetype.lower().split("/")

    try:
        return MediaType(mime_prefix)
    except ValueError as exc:
        if not validate:
            return None

        raise ValueError(
            f"unhandled media type for media at {media_filepath!s} "
            f"(mimetype: {mimetype!s})"
        ) from exc
