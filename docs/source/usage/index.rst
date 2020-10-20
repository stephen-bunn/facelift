.. _usage:

=====
Usage
=====

Before we get started learning how to use the methods provided by :ref:`facelift`, we
have some basic terminology to define.
The :mod:`~facelift.types` module provides these following types/terms which we use
throughout the package.
We use these terms though most of our documentation, so make sure you take a peek at the
responsibility of these names.

* | :attr:`~facelift.types.Frame`
  | Defines a single matrix of pixels representing an image (or a single frame).
  | Represented by a :class:`numpy.ndarray` using the shape ``(Any, Any, 3)`` of type
      :data:`numpy.uint8`.
  | These frames are pulled out of some media or stream and is used as the source
      content to try and detect faces from.

* | :attr:`~facelift.types.Point`
  | Describes an (x, y) coordinate relative to a specific frame.
  | Represented by a :class:`numpy.ndarray` of shape ``(2,)`` of type
      :data:`numpy.int64`.

* | :attr:`~facelift.types.PointSequence`
  | Describes a sequence of points that typically define a feature.
  | Represented by a :class:`numpy.ndarray` of shape ``(Any, 2)`` of type
      :data:`numpy.int64`.

* | :class:`~facelift.types.FaceFeature`
  | An enum of available face features to detect (such as an eye or the nose).
  | Represented by a :attr:`~facelift.types.PointSequence`.

* | :class:`~facelift.types.Face`
  | Defines a detected face containing the landmarks and bounding frame of the face.
  | Represented by a custom :func:`dataclasses.dataclass` using a dictionary of
      :class:`~facelift.types.FaceFeature` to :attr:`~facelift.types.PointSequence`
      to describe the detected face features.

* | :attr:`~facelift.types.Encoding`
  | Describes an encoded face frame that can later be used to recognize the same face.
  | Represented by a :class:`numpy.ndarray` of shape ``(128,)`` of type
      :data:`numpy.int64`

----

.. include:: reading-frames.rst

----

.. include:: rendering-frames.rst

----

.. include:: transforming-frames.rst

----

.. include:: detecting-faces.rst

----

.. include:: drawing-faces.rst

----

.. include:: recognizing-faces.rst
