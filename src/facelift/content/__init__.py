# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains mechanisims for extracting frames from some media content."""

from .capture import iter_media_frames, iter_stream_frames

__all__ = ["iter_media_frames", "iter_stream_frames"]
