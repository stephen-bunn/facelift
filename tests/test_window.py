# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains tests related to the provided OpenCV window context manager."""

import operator
from typing import List, Optional
from unittest.mock import call, patch

import pytest
from hypothesis import given
from hypothesis.strategies import (
    integers,
    just,
    lists,
    none,
    one_of,
    sampled_from,
    text,
)

from facelift.types import Frame
from facelift.window import (
    DEFAULT_WINDOW_DELAY,
    DEFAULT_WINDOW_STEP_KEY,
    DEFAULT_WINDOW_TITLE,
    WindowStyle,
    opencv_window,
)

from .strategies import frame


def test_opencv_window_default():
    # XXX: simple sanity check to ensure that breaking changes are not introduced for
    # OpenCV windows between version bumps
    window = opencv_window()
    assert window.title == DEFAULT_WINDOW_TITLE
    assert window.delay == DEFAULT_WINDOW_DELAY
    assert window.step_key == DEFAULT_WINDOW_STEP_KEY


@given(one_of(none(), just("")))
def test_opencv_window_validates_title(title: Optional[str]):
    with pytest.raises(ValueError):
        opencv_window(title=title)


@given(one_of(none(), integers(max_value=0)))
def test_opencv_window_validates_delay(delay: Optional[int]):
    with pytest.raises(ValueError):
        opencv_window(delay=delay)


def test_opencv_window_context():
    window = opencv_window()
    with patch.object(window, "create") as mocked_create, patch.object(
        window, "close"
    ) as mocked_close:
        with window:
            pass

        mocked_create.assert_called_once()
        mocked_close.assert_called_once()


def test_opencv_window_create_uses_defaults():
    with patch("facelift.window.cv2") as mocked_cv2:
        opencv_window().create()

        mocked_cv2.namedWindow.assert_called_once_with(
            winname=DEFAULT_WINDOW_TITLE, flags=WindowStyle.DEFAULT
        )


@given(
    text(min_size=1),
    lists(sampled_from(WindowStyle.__all__), min_size=2, max_size=2, unique=True),
)
def test_opencv_window_create(title: str, style: List[int]):
    window_style = operator.or_(*style)
    with patch("facelift.window.cv2") as mocked_cv2:
        opencv_window(title=title, style=window_style).create()

        mocked_cv2.namedWindow.assert_called_once_with(
            winname=title,
            flags=window_style,
        )


def test_opencv_window_close_uses_defaults():
    with patch("facelift.window.cv2") as mocked_cv2:
        opencv_window().close()

        mocked_cv2.destroyWindow.assert_called_once_with(winname=DEFAULT_WINDOW_TITLE)


@given(text(min_size=1))
def test_opencv_window_close(title: str):
    with patch("facelift.window.cv2") as mocked_cv2:
        opencv_window(title=title).close()

        mocked_cv2.destroyWindow.assert_called_once_with(winname=title)


@given(frame())
def test_opencv_window_render(test_frame: Frame):
    with patch("facelift.window.cv2") as mocked_cv2:
        window = opencv_window()
        window.render(test_frame)

        mocked_cv2.imshow.assert_called_once_with(
            winname=DEFAULT_WINDOW_TITLE, mat=test_frame
        )
        mocked_cv2.waitKey.assert_called_once_with(delay=DEFAULT_WINDOW_DELAY)


@given(frame(), integers(min_value=0, max_value=32))
def test_opencv_window_render_allows_step(test_frame: Frame, step_key: int):
    with patch("facelift.window.cv2") as mocked_cv2:
        window = opencv_window(step=True, step_key=step_key)
        # the mocked side effects here is to compensate for:
        # 1. the first call to `waitKey` for the actual frame delay
        # 2. the first call to `waitKey` in step to ensure `continue` is reached
        # 3. the second call to `waitKey` to ensure step is exited on propery keypress
        mocked_cv2.waitKey.side_effect = [None, None, step_key]

        window.render(test_frame)
        mocked_cv2.waitKey.assert_has_calls(
            [call(delay=window.delay), call(delay=0), call(delay=0)]
        )
