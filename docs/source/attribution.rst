.. _attribution:

===========
Attribution
===========

A lot of the logic that makes up this package is pulled from other projects or is using
resources that other developers have produced.
Below are callouts to the projects or resources that were used to create this package.

| **Facelift Icon**
| — Created by **Delwar Hossain** pulled from
   `Noun Project <https://thenounproject.com/>`_

| **81 Point Face Feature Model**
| — Created by **codeniko** pulled from
   `codeniko/shape_predictor_81_face_landmarks
   <https://github.com/codeniko/shape_predictor_81_face_landmarks>`_
| This model is used as part of the :class:`~facelift.detect.landmark.FullFaceDetector`
   to allow for detecting the :attr:`~facelift.types.FaceFeature.FOREHEAD` feature.
   Thanks to codeniko for traning this model.

| **Image Transformation Utilities**
| — Created by **josebr1** pulled from
   `josebr1/imutils <https://github.com/jrosebr1/imutils>`_
| A load of utilities and image transformations were inspired by and sometimes directly
   pulled the work done in this project. Thanks to all the contributors who threw these
   together. It made refactoring them to fit for my own design and use-case much easier.

| **Facial Recognition**
| —  Created by **ageitgey** pulled from
   `ageitgey/face_recognition <https://github.com/ageitgey/face_recognition>`_
| A fair chunk of the logic used for facial recognition was inspired from the work done
   in this project. Thanks to all the contributors who worked on building this iteration
   of a facial recognition package.
