Rendering Frames
================

Now that we are reading frames in, we probably want to be able to preview what is going
to be processed.
OpenCV provides a *semi-decent* window utility that we take advantage of for our basic
frame preview.
If you want to display these frames in a more production-level applciation, I would
recommend looking into using a canvas powered by OpenGL instead of relying on the hacky
and inflexible solution provided by OpenCV.

   It is not within the scope of this project to provide an optimial canvas for
   displaying the frames read in through OpenCV.
   There are likely other projects out there that can display frames (numpy pixel
   arrays) or a transformed variant of this frame while taking advantage of the GPU.

Regardless, for our use cases we only want to be able to quickly and cheaply preview
the frames we are processing.
To help with this, we provide a :class:`~.window.opencv_window` context manager that
will create a temporary window that can be used for rendering these captured frames.

.. code-block:: python
  :linenos:

  from facelift.capture import iter_media_frames
  from facelift.window import opencv_window

  with opencv_window() as window:
      for frame in iter_stream_frames():
          window.render(frame)


Here is a quick screen capture running the above example.

.. raw:: html

   <video style="width:100%;" controls>
      <source src="../_static/assets/recordings/basic_opencv_window.mp4" type="video/mp4">
   </video>


Note that since this window helper is a context manager, the window will destroy itself
once there are no more frames to process and we break out of the frame generator.
In the above example, I am simply raising a :class:`KeyboardInterrupt` by pressing
``Ctrl+C``, but you can be much more clever about it in your usage.

Customization
-------------

There are several available options that allow you to *slightly* tweak the created
window.
The options are fairly limited as we are just forwarding the desired tweaks to the
creation of the window in OpenCV.
*Don't expect much in terms of flexibility of customization for these windows.*

Window Title
~~~~~~~~~~~~

| By default, we throw a "Facelift" title on the created window.
| You can override this by passing in a ``title`` to the context manager:

.. code-block:: python
   :linenos:

   with opencv_window(title="My Window") as window:
       ...

This title will be used to also destroy the window as OpenCV naively destroys windows
based on window titles.
This isn't such a big issue as OpenCV (and in turn the :class:`~.window.opencv_window`
manager) doesn't allow mutation of a window title once the window is opened.

Window Style
~~~~~~~~~~~~

OpenCV windows have several different style features they can pick and choose from.
These features are defined in the :class:`~.window.WindowStyle` object and can be joined
together with the boolean ``|`` and passed through to the ``style`` parameter.

.. code-block:: python
   :linenos:

   from facelift.window import opencv_window, WindowStyle

   with opencv_window(style=WindowStyle.GUI_EXPANDED | WindowStyle.KEEP_RATIO) as window:
      ...


By default the window will use the :attr:`~.window.WindowStyle.DEFAULT` window style
which is a combination of some of other available window styles.
If you actually need to use a custom window style, I encourage that you play around with
these options yourself to see what works best for you.

Display Delay
~~~~~~~~~~~~~

The delay at which OpenCV attempts to render frames is another feature that can be
controlled.
This is fairly useful when you want to slow down the frames being rendered in the window
rather than the speed at which frames are being read.
This delay is defined in milliseconds as an integer and is defaulted to 1.

.. code-block:: python
   :linenos:

   from facelift.capture import iter_stream_frames
   from facelift.window import opencv_window

   with opencv_window(delay=1000) as window:  # wait 1 second between displaying frames
       for frame in iter_stream_frames():
           window.render(frame)


Note that you can also handle do this yourself with a simple :func:`time.sleep` prior or
post a :meth:`~.window.opencv_window.render` call.
That solution may be a better path forward if you are running into issues with the
``delay`` parameter.

.. warning::
   This delay **must** be greater than 0.
   We have a validation step in the creation of the window to ensure that it is not
   initialized to 0.
   However, you can still get around this initial check by setting ``delay`` on the
   created window context instance.
   For example, you can *technically* do the following:

   >>> from facelift.window import opencv_window
   >>> with opencv_window(delay=1) as window:
   ...   window.delay = 0

   This will very likely break the frame rendering as OpenCV will enter a waiting state
   with no refresh interval when the window delay is set to 0.


Display Step
~~~~~~~~~~~~

Sometimes you want to pause on each frame to *essentially* prompt for user interaction
when rendering frames.
This feature is particularly useful when attempting to render single frames (such as
those from images) as the generator will immediately exit and could exit the window
context manager which will destroy the window.

For example, the following sample will immediately create a window and then quickly
close it as the :func:`~.capture.iter_media_frames` generator will immediately read the
image and immediately exit the window's context manager:

.. code-block:: python
   :linenos:

   with opencv_window() as window:
       for frame in iter_media_frames(Path("~/my-image.jpeg")):
           window.render(frame)


If you would like to force the window to await user input to render the next frame
every time :meth:`~.window.opencv_window.render` is called, you can use the ``step`` and
``step_key`` arguments.

.. code-block:: python
   :linenos:

   with opencv_window(step=True, step_key=0x20) as window:
       ...

In the above example, since we have enabled ``step`` and defined the step key to be
``0x20``, our window will wait for the user to press [Space] (ASCII 36 or 0x20) before
rendering the next frame.
