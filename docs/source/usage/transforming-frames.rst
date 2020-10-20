Transforming Frames
===================

When detecting faces we start hitting bottlenecks quite quickly.
The more pixels you have to process, the slower face detection takes.
To help make frames easier to manage for face detection, we supply a few frame
transformation functions.

.. figure:: ../_static/assets/images/transform-flow.png
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
