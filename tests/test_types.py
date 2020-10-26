# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains tests for the types module."""

import numpy
from hypothesis import given

from facelift.types import Face

from .strategies import face


@given(face())
def test_Face_rectangle(face: Face):
    rectangle = face.rectangle
    assert isinstance(rectangle, numpy.ndarray)
    assert rectangle.shape == (
        2,
        2,
    )

    start = face.raw.rect.tl_corner()
    assert (rectangle[0] == [start.x, start.y]).all()

    end = face.raw.rect.br_corner()
    assert (rectangle[-1] == [end.x, end.y]).all()
