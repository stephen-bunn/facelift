.. _OpenCV: https://docs.opencv.org/3.4/modules.html

Transforming Frames
===================

Before we get to actually detecting faces, it would benefit us to know what kind of
bottlenecks we will hit and how we can avoid or reduce them.

The obvious bottleneck any kind of object detection is that the more pixels you have to
process, the longer object detection takes.
To reduce this we typically want to scale down large frames so that we don't waste so
much time looking through all the available pixels.
This scaling operation is provided as a transformation function
:func:`~.transform.scale`.

.. code-block:: python
   :linenos:

   from facelift.capture import iter_stream_frames
   from facelift.transform import scale

   for frame in iter_stream_frames():
       assert frame.shape[0] == 128
       frame = scale(frame, 0.5)
       assert frame.shape[0] == 64


By scaling down the frame to a more reasonable size, feature detection will be able to
perform much quicker as we have less pixels to run through.
This is just one example of how we can reduce bottlenecks to benefit feature detection.
However, there are many more transformations that we *might* need to do to benefit
``dlib``'s frontal face detector.

For example, what if we are processing a video shot in portrait but we are reading in
frames in landscape?
We will probably need to rotate the frame to be in portrait mode so that the faces we
are trying to detect are positioned top-down in the frame instead of left-right.
We can also do this using a provided transformation :func:`~.transform.rotate`.

Let's say we want to rotate these frames -90 degrees:

.. code-block:: python
   :linenos:

   from facelift.capture import iter_stream_frames
   from facelift.transform import rotate

   for frame in iter_stream_frames():
       frame = rotate(frame, -90)


For a full list of the available transformations we supply, I recommend you look
through the :mod:`~.transform` module's auto-built documentation.

The goal of this module is to provide the basic transformations that you may need to
optimize face detection using our methods.
You may run into a use case where you need something we do not provide in this module.
In this case, you likely can find what you need already built into OpenCV_.


Chaining Transforms
-------------------

Most of the time you will end up with several necessary transformations to get the frame
in a position that is optimal for face detection.
In these cases, it's fairly straightforward to compose multiple transforms together
through the following type of composition:

.. code-block:: python
   :linenos:

   from facelift.capture import iter_stream_frames
   from facelift.transform import scale, flip, rotate
   from facelift.window import opencv_window

   with opencv_window() as window:
       for frame in iter_stream_frames():
           frame = rotate(flip(scale(frame, 0.35), x_axis=True), 90)
           window.render(frame)


In this example, we are first scaling down the frame to 35%, flipping the frame on the
x-axis, and the rotating it by +90 degrees.
Potentially useful for large, inverted media files where faces are aligned left to right
rather than top-down.
Internally the frame is going through each transformation just as you would expect.

.. figure:: ../_static/assets/images/transform-flow.png
   :width: 75%
   :align: center

   Sample Transform Flow


This was just a quick overview of the concept of transforming frames before we attempt to
detect face features.
We will see more explicitly how transformations benefit feature detection in the next
section.
