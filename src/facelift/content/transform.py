# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains some common necessary frame transformation helper methods.

Attributes:
    DEFAULT_INTERPOLATION (int):
        The default type of interpolation to use in transforms that require an
        interpolation method. Defaults to ``cv2.INTER_AREA``.
"""

import warnings
from typing import Optional, Tuple

import cv2
import numpy

from ..types import Frame

DEFAULT_INTERPOLATION: int = cv2.INTER_AREA


def copy(frame: Frame) -> Frame:
    """Copy the given frame to a new location in memory.

    Examples:
        >>> from facelift.content.transform import copy
        >>> copied_frame = copy(frame)
        >>> assert frame == copied_frame
        >>> assert frame is not copied_frame

    Args:
        frame (:attr:`~.types.Frame`): The frame to copy

    Returns:
        :attr:`~.types.Frame`: An exact copy of the given frame
    """

    return frame.copy()


def scale(
    frame: Frame, factor: float, interpolation: int = DEFAULT_INTERPOLATION
) -> Frame:
    """Scale a given frame down or up depending on the given scale factor.

    Examples:
        Downscaling a frame can be performed with a ``scale`` factor >0 and <1.
        For example, scaling a frame to half of its original size would require a scale
        factor of 0.5.

        >>> from facelift.content.transform import scale
        >>> assert frame.shape[:1] == [512, 512]
        >>> downscaled_frame = scale(frame, 0.5)
        >>> assert downscaled_frame.shape[:1] == [256, 256]

        Upscaling a frame with this method is **very** naive and unoptimal.
        However, any value >1 will result in a upscaled frame.
        For example, scaling a frame to double its original size would require a scale
        factor of 2.

        >>> from facelift.content.transform import scale
        >>> assert frame.shape[:1] == [512, 512]
        >>> upscaled_frame = scale(frame, 2)
        >>> assert upscaled_frame.shape[:1] == [1024, 1024]

        Following this logic, a scale factor of 1 would result in absolutely no change
        to the given frame.

    .. warning::
        This transformation will return the **exact same frame instance** as the one
        provided through the ``frame`` parameter in the following cases:

            1. If a factor of exactly ``1`` is given.
               In this case the scale operation would result in no change.

            2. The given frame has factor less than ``1`` a width or height of 1px.
               In this case we are attempting to scale down the given frame and we
               cannot scale down the frame any further without producing a 0px frame.

    Args:
        frame (:attr:`~.types.Frame`): The frame to scale
        factor (float): The factor to scale the given frame
        interpolation (Optional[int], optional):
            The type of interpolation to use in the scale operation.
            Defaults to :attr:`~DEFAULT_INTERPOLATION`.

    Raises:
        ValueError: When the given scale factor is not positive

    Returns:
        :attr:`~.types.Frame`: The newly scaled frame
    """

    if factor <= 0:
        raise ValueError(
            f"Factor should be a positive floating point, received {factor!r}"
        )

    if factor == 1:
        return frame

    height, width, *_ = frame.shape
    if factor < 1 and (height == 1 or width == 1):
        return frame

    return cv2.resize(
        src=frame,
        dsize=None,
        fx=factor,
        fy=factor,
        interpolation=interpolation,
    )


def resize(
    frame: Frame,
    width: Optional[int] = None,
    height: Optional[int] = None,
    lock_aspect: bool = True,
    interpolation: int = DEFAULT_INTERPOLATION,
) -> Frame:
    """Resize a given frame to a given width and/or height.

    * If both width and height are given, the frame will be resized accordingly.
    * If only one of width or height is given, the frame will be resized according to
      the provided dimension (either width or height).

        * As long as ``lock_aspect`` is truthy, the unprovided dimension will be
          adjusted to maintain the original aspect-ratio of the frame.
        * If ``lock_aspect`` is falsy, the resize operation will only scale the provided
          dimension while keeping the original size of the unprovided dimension.

    Examples:
        Resize a frame's width while keeping the height relative:

        >>> from facelift.content.transform import resize
        >>> assert frame.shape[:1] == [512, 512]
        >>> resized_frame = resize(frame, width=256, lock_aspect=True)
        >>> assert resized_frame.shape[:1] == [256, 256]

        Resize a frame's width while keeping the original height:

        >>> from facelift.content.transform import resize
        >>> assert frame.shape[:1] == [512, 512]
        >>> resized_frame = resize(frame, width=256, lock_aspect=False)
        >>> assert resized_frame.shape[:1] == [512, 256]

        Resize both a frame's width and height:

        >>> from facelift.content.transform import resize
        >>> assert frame.shape[:1] == [512, 512]
        >>> resized_frame = resize(frame, width=256, height=128)
        >>> assert resized_frame.shape[:1] == [128, 256]

    Args:
        frame (:attr:`~.types.Frame`):
            The frame to resize
        width (Optional[int], optional):
            The exact width to resize the frame to.
        height (Optional[int], optional):
            The exact height to resize the frame to.
        lock_aspect (bool, optional):
            Whether to keep the width and height relative when only given one value.
            Defaults to True.
        interpolation (int, optional):
            The type of interpolation to use in the resize operation.
            Defaults to :attr:`~DEFAULT_INTERPOLATION`.

    Returns:
        :attr:`~.types.Frame`: The newly resized frame
    """

    if width == 0 or height == 0:
        raise ValueError("Cannot resize frame to a width or height of 0")

    if width is None and height is None:
        return frame

    if width and height:
        return cv2.resize(
            src=frame,
            dsize=(width, height),
            fx=None,
            fy=None,
            interpolation=interpolation,
        )

    frame_height, frame_width, *_ = frame.shape
    if not lock_aspect:
        return cv2.resize(
            src=frame,
            dsize=(width or frame_width, height or frame_height),
            fx=None,
            fy=None,
            interpolation=interpolation,
        )

    if height is not None:
        relative_width = int(frame_width * (height / float(frame_height))) or 1
        return cv2.resize(
            src=frame,
            dsize=(relative_width, height),
            fx=None,
            fy=None,
            interpolation=interpolation,
        )
    elif width is not None:
        realative_height = int(frame_height * (width / float(frame_width))) or 1
        return cv2.resize(
            src=frame,
            dsize=(width, realative_height),
            fx=None,
            fy=None,
            interpolation=interpolation,
        )

    return frame  # pragma: no cover


def rotate(
    frame: Frame, degrees: int, interpolation: int = DEFAULT_INTERPOLATION
) -> Frame:
    """Rotate a frame while keeping the whole frame visible.

    Examples:
        >>> from facelift.content.transform import rotate
        >>> rotated_90 = rotate(frame, 90)
        >>> rotated_neg_90 = rotate(frame, -90)

    .. warning::
        This transform typically will produce larger frames since we are producing a
        rotated frame while keeping the original frame completely visible.
        This means if we do a perfect 45 degree rotation on a 512x512 frame we will
        produce a 724x724 frame since the 512x512 frame is now on a angle that requires
        a larger container.

        Be cautious when using rotation.
        Most of the time you do not need to rotate on any angles other than 90, 180, and
        270 for decent face detection.
        However, this isn't *always* true.

    Args:
        frame (:attr:`~.types.Frame`):
            The frame to rotate
        degrees (int):
            The number of degress to rotate the given frame
        interpolation (int, optional):
            The type of interpolation to use in the produced rotation matrix.
            Defaults to :attr:`~DEFAULT_INTERPOLATION`.

    Returns:
        :attr:`~.types.Frame`: The newly rotated frame
    """

    if abs(degrees) in (0, 360):
        return frame

    frame_height, frame_width, *_ = frame.shape
    center_x, center_y = frame_width / 2, frame_height / 2

    rotation_matrix = cv2.getRotationMatrix2D(
        center=(center_x, center_y), angle=-degrees, scale=1.0
    )

    cos = numpy.abs(rotation_matrix[0, 0])
    sin = numpy.abs(rotation_matrix[0, 1])

    new_width = int((frame_height * sin) + (frame_width * cos))
    new_height = int((frame_height * cos) + (frame_width * sin))

    rotation_matrix[0, 2] += (new_width / 2) - center_x
    rotation_matrix[1, 2] += (new_height / 2) - center_y

    return cv2.warpAffine(
        src=frame,
        M=rotation_matrix,
        dsize=(new_width, new_height),
        flags=interpolation,
    )


def crop(frame: Frame, start: Tuple[int, int], end: Tuple[int, int]) -> Frame:
    """Crop the given frame between two top-left to bottom-right points.

    Examples:
        Crop a frame from the first pixel to the center pixel.

        >>> from facelift.content.transform import crop
        >>> assert frame.shape[:1] == [512, 512]
        >>> cropped_frame = crop(frame, (0, 0), (256, 256))
        >>> assert cropped_frame.shape[:1] == [256, 256]

    Args:
        frame (:attr:`~.types.Frame`):
            The frame to crop
        start (Tuple[int, int]):
            The top-left point to start the crop at
        end (Tuple[int, int]):
            The bottom-right point to end the crop at

    Raises:
        ValueError:
            When the given starting crop point appears after the given ending crop point

    Returns:
        :attr:`~.types.Frame`: The newly cropped frame
    """

    left, top = start
    right, bottom = end

    if right <= left or bottom <= top:
        raise ValueError(
            "Starting crop point cannot be greater than the ending crop point, "
            f"(start={start}, end={end})"
        )

    width = right - left
    height = bottom - top
    return frame[top : top + height, left : left + width]


def translate(
    frame: Frame,
    delta_x: Optional[int] = None,
    delta_y: Optional[int] = None,
    interpolation: int = DEFAULT_INTERPOLATION,
) -> Frame:
    """Translate the given frame a specific distance away from its origin.

    Examples:
        >>> from facelift.content.transform import translate
        >>> translated_neg_90_x_frame = translate(frame, delta_x=-90)

    .. important::
        This translation retains the original size of the given frame.
        So a 512x512 frame translated 90px on the x-axis will still be 512x512 and space
        where the frame use to take up will be essentially nulled out.

    Args:
        frame (:attr:`~.types.Frame`):
            The frame to translate
        delta_x (Optional[int], optional):
            The pixel distance to translate the frame on the x-axis.
        delta_y (Optional[int], optional):
            The pixel distance to translate the frame on the y-axis.
        interpolation (int, optional):
            The type of interpolation to use during the translation.
            Defaults to :attr:`~DEFAULT_INTERPOLATION`.

    Returns:
        :attr:`~.types.Frame`: The newly translated frame
    """

    if delta_x is None and delta_y is None:
        return frame

    translation_matrix = numpy.float32([[1, 0, delta_x or 0], [0, 1, delta_y or 0]])
    frame_height, frame_width, *_ = frame.shape

    return cv2.warpAffine(
        src=frame,
        M=translation_matrix,
        dsize=(frame_width, frame_height),
        flags=interpolation,
    )


def grayscale(frame: Frame) -> Frame:
    """Convert the given frame to grayscale.

    This helper is useful *sometimes* for classification as color doesn't matter as much
    during face encoding.

    Examples:
        >>> from facelift.content.transform import grayscale
        >>> grayscale_frame = grayscale(bgr_frame)

    Args:
        frame (:attr:`~.types.Frame`): The BGR frame to convert to grayscale

    Returns:
        :attr:`~.types.Frame`: The newly grayscaled frame
    """

    return cv2.cvtColor(src=frame, code=cv2.COLOR_BGR2GRAY)


def rgb(frame: Frame) -> Frame:
    """Convert the given frame to RGB.

    This helper transform is typically needed when working with other image processing
    libraries such as `pillow <https://pillow.readthedocs.io/en/stable/>`_ as they work
    in RGB coordinates while OpenCV works in BGR coordinates.

    Examples:
        >>> from facelift.content.transform import rgb
        >>> rgb_frame = rgb(bgr_frame)

    Args:
        frame (:attr:`~.types.Frame`): The BGR frame to conver to RGB

    Returns:
        :attr:`~.types.Frame`: The new RGB frame
    """

    return cv2.cvtColor(src=frame, code=cv2.COLOR_BGR2RGB)
