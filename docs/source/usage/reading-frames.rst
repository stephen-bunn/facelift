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

.. figure:: ../_static/assets/images/capture-flow.png
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
