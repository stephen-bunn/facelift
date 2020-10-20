.. _dlib: http://dlib.net/python/

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
