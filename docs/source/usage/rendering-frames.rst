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
      <source src="../_static/assets/recordings/basic_opencv_window.mp4" type="video/mp4">
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
