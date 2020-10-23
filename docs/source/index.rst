.. raw:: html

   <div class="Facelift_Container">
      <img class="Facelift_Image" alt="Facelift" src="_static/assets/images/facelift-icon.png"/>
      <div class="Facelift_Content">
         <div class="Facelift_Title">Facelift</div>
         <div class="Facelift_Description">
            A simple wrapper for face feature detection and recognition.
         </div>
         <div class="Facelift_Badges">
            <a href="https://pypi.org/project/facelift/" target="_blank">
               <img alt="Supported Versions" src="https://img.shields.io/pypi/pyversions/facelift.svg" />
            </a>
            <a href="https://github.com/stephen-bunn/facelift/actions?query=workflow%3A%22Test+Package%22" target="_blank">
               <img alt="Test Status" src="https://github.com/stephen-bunn/facelift/workflows/Test%20Package/badge.svg" />
            </a>
            <a href="https://codecov.io/gh/stephen-bunn/facelift" target="_blank">
               <img alt="Coverage" src="https://codecov.io/gh/stephen-bunn/facelift/branch/master/graph/badge.svg?token=xhhZQr8l76" />
            </a>
            <a href="https://github.com/ambv/black" target="_blank">
               <img alt="Code Style: Black" src="https://img.shields.io/badge/code%20style-black-000000.svg" />
            </a>
         </div>
      </div>
   </div>


Several personal projects I've had in the past relied on some basic face feature
detection either for face isolation, face state detection, or some kinds of perspective
estimation.
I found that there are plenty of resources for learning how to perform face detection in
Python, but most of them suffer from a handful of the following issues:

1. Isn't easy to use right out of the box.
2. Doesn't provide face feature detection, just simple face detection.
3. Relies on older and no-longer maintained methods from ``cv2`` for face detection.
4. Is pretty greedy in terms of memory usage and scattered method calls.
5. Doesn't provide a selection of helpers to make face detection easier and quicker.
6. Requires that you write a whole bunch of boilerplate to get anything clean looking.
7. Or just my own personal disagreements with some of the code structure.

This project is my own attempt to provide decent face feature detection when you don't
want to think too hard about it.
We try to get as close as possible to a single ``pip`` install and still provide
effective detection and recognition in Python.
However, we do have several system dependencies that are necessary, see
:ref:`system-requirements` for more details.

Below is a simple example of full face feature detection and rendering out to a standard
OpenCV_ window using some of the features available in Facelift.
**To get started using this package, please see the** :ref:`getting-started` **guide.**

.. literalinclude:: _static/assets/examples/basic_face_detection.py
   :linenos:

.. image:: _static/assets/recordings/basic_face_detection.gif


User Documentation
------------------

.. toctree::
   :maxdepth: 1

   getting-started
   usage/index
   contributing
   code-of-conduct
   changelog
   license
   attribution


Project Reference
-----------------

.. toctree::
   :maxdepth: 2

   facelift
