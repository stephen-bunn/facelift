# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains generic composite strategies for package tests."""

from pathlib import Path
from string import printable

from hypothesis.strategies import SearchStrategy, composite, just, lists, text


@composite
def pathlib_path(draw) -> SearchStrategy[Path]:
    """Composite strategy for buliding a random :class:`~pathlib.Path` instance."""

    return draw(
        just(Path(*draw(lists(text(alphabet=printable, min_size=1), min_size=1))))
    )
