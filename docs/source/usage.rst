.. _dlib: http://dlib.net/python/
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
  | Represented by a :class:`numpy.ndarray` of shape (2) of type :data:`numpy.int64`.

* | :attr:`~facelift.types.PointSequence`
  | Describes a sequence of points that typically define a feature.
  | Represented by a :class:`numpy.ndarray` of shape (Any, 2) of type
      :data:`numpy.int64`.

* | :class:`~facelift.types.FaceFeature`
  | An enum of available face features to detect (such as an eye or the nose).
  | Represented by a :attr:`~facelift.types.PointSequence`.

* | :class:`~facelift.types.Face`
  | Defines a detected face containing the landmarks and bounding frame of the face.
  | Represented by a custom :func:`dataclasses.dataclass` using a dictionary of
      :class:`~facelift.types.FaceFeature` to :attr:`~facelift.types.PointSequence`
      to describe the detected face features.

----

Reading Frames
==============

The first step to detecting faces is being able to extract the frames from some media.
The content that we typically want to extract frames from are defined in
:class:`~.types.MediaType`.

.. autoclass:: facelift.types.MediaType
   :noindex:

Typically this process is performed using a mix of OpenCV functions that use completely
different syntax for each of these types of media.
For the purposes of this project, we really shouldn't care about the differences of how
OpenCV opens, processes, and closes media.
So we reduced this process and namespaced it within the :mod:`~.capture` module.

This module's overall purpose is to effeciently encapsulate the OpenCV calls necessary
to capture the frames from the given media.

.. figure:: _static/assets/images/capture-flow.png
   :width: 75%
   :align: center

   Basic Capture Flow


To do this we have exposed separate generator functions.
One for handling written media files, and another for handling streamed frames.
We made the decision to keep these generators separate as they have distinct features
that would make a single generator function less explicit and intuitive.

Capturing Media Frames
----------------------

Reading frames from existing media files (either images or videos), you can utilize the
:func:`~.capture.iter_media_frames` generator to extract frames.
This function takes a :class:`pathlib.Path` instance and will build the appropriate
generator to capture and iterate over the available frames one at a time.

.. code-block:: python
   :linenos:

   from facelift.capture import iter_media_frames
   from facelift.types import Frame

   for frame in iter_media_frames(Path("~/my-video.mp4")):
      assert isinstance(frame, Frame)


If you would like to loop over the available frames, the ``loop`` boolean flag can be
set to ``True``.

.. code-block:: python
  :linenos:

  for frame in iter_media_frames(Path("~/my-video.mp4"), loop=True):
      assert isinstance(frame, Frame)


This flag will seek to the starting frame automatically once all frames have been read
essentially restarting the generator.
This means that you will need to break out of the generator yourself as it will produce
an infinite loop.

Capturing Stream Frames
-----------------------

Reading frames from a stream such as a webcam, you can utilize the very similar
:func:`~.capture.iter_stream_frames` generator to extract frames.
This function will scan for the first available active webcam to stream frames from.

.. code-block:: python
  :linenos:

  from facelift.capture import iter_stream_frames
  from facelift.types import Frame

  for frame in iter_stream_frames():
      assert isinstance(frame, Frame)


If you happen to have 2 webcams available, you can pick what webcam to stream frames
from by using the indexes (0-99).
If you wanted to stream frames from the second available webcam, simply pass in index
``1`` to the generator:

.. code-block:: python
  :linenos:

  for frame in iter_stream_frames(1):
      assert isinstance(frame, Frame)


.. important::
  When capturing streamed frames, this generator will not stop until the device stream
  is halted.
  Typically, when processing stream frames, you should build in a mechanism to break out
  of the capture loop when desireable.
  More information on this is discussed in the next section.

----

Rendering Frames
================

Now that you have the ability to capture frames from media, we need a way to display the
frames so we can view what we are processing.
OpenCV provides a *decent* window provider that we take advantage of for our basic
frame preview.
If you want to display these frames in a more production-level applciation, I would
recommend looking into using a canvas powered by OpenGL.

For our use case, we can use the provided :class:`~.window.opencv_window` context
manager to create a window that we can use for rendering our captured frames.

.. code-block:: python
  :linenos:

  from facelift.capture import iter_media_frames
  from facelift.window import opencv_window

  with opencv_window() as window:
      for frame in iter_stream_frames():
          window.render(frame)


.. raw:: html

   <video style="width:100%;" controls>
      <source src="_static/assets/recordings/basic_opencv_window.mp4" type="video/mp4">
   </video>


Since this window helper is a context manager, the window will destroy itself once there
are no more frames to process and we break out of the frame generator.

There are several available options that allow you to *slightly* tweak the created
window.
By default, we throw the "Facelift" title on the created window.
You can override this by passing in a ``title`` to the context manager:

.. code-block:: python
   :linenos:

   with opencv_window(title="My Window") as window:
       ...

By default, the window will display frames as fast as the
:meth:`~.window.opencv_window.render` method is called.
If you would like to force the window to await user input to render the next frame
everytime render is called, you can use the ``step`` and ``step_key`` arguments.

.. code-block:: python
   :linenos:

   with opencv_window(step=True, step_key=0x20) as window:
       ...

Since we have defined the step key to be ``0x20``, our window will wait for the user to
press [Space] (ASCII 36 or 0x20) before rendering the next frame.
This feature is particularly useful when you want to preview the results of face
detection from an image before immediately destroying the window.

There are a few other options that you may find useful when trying to preview frames.
I recommend you checkout the documentation for :class:`~.window.opencv_window` to see
what is available.

----

Transforming Frames
===================

When detecting faces we start hitting bottlenecks quite quickly.
The more pixels you have to process, the slower face detection takes.
To help make frames easier to manage for face detection, we supply a few frame
transformation functions.

.. figure:: _static/assets/images/transform-flow.png
   :width: 75%
   :align: center

   Sample Transform Flow


Each of these transforms takes a single frame, mutates it with some options, and returns
it.


.. code-block:: python
   :linenos:

   from facelift.capture import iter_stream_frames
   from facelift.transform import scale, flip, rotate
   from facelift.window import opencv_window

   with opencv_window() as window:
       for frame in iter_stream_frames():
           frame = rotate(flip(scale(frame, 0.35), x_axis=True), 90)
           window.render(frame)

----

Detecting Faces
===============

Detection of faces is done through the power of dlib_.
We have included some pre-trained models for various face features.

.. code-block:: python
   :linenos:

   from facelift.detect import BasicFaceDetector

   detector = BasicFaceDetector()
   for frame in iter_stream_frames():
       for face in detector.iter_faces(frame):
           print(face)

----

Drawing Face Features
=====================

----

Recognizing Faces
=================
