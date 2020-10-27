.. _changelog:

=========
Changelog
=========

| All notable changes to this project will be documented in this file.
| The format is based on `Keep a Changelog <http://keepachangelog.com/en/1.0.0/>`_ and this project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`_.
|

.. towncrier release notes start

`0.1.0 <https://github.com/stephen-bunn/facelift/releases/tag/v0.1.0>`_ (*2020-10-27*)
======================================================================================

Miscellaneous
-------------

- The initial release doesn't have a super detailed list of introduced features or
  bugfixes as this project was pulled together from other side projects I've had in the
  past.
  Below I'll list the important features that we are starting out with.
  Future additions should result in a history of news fragments that get aggregated into
  this changelog.

  Starting features:

  1. Face feature detection with a few bundled models.
      * Basic face feature detection (eyes and nose)
      * Partial face feature detection (trained model produced by ``dlib``)
      * Full face feature detection (third party trained model)
  2. Face recognition with a bundled ResNet produced by ``dlib`` to produce face encoding.
      * Includes basic Euclidean distance scoring to find similar faces.
  3. Wrappers for OpenCV frame capturing.
      * Generators for frames from written media files.
      * Generators for frames from streaming devices (webcams).
  4. Wrappers for OpenCV windows.
      * Context managers for named window management.
  5. Wrappers for OpenCV common frame transformations
      * Scaling, resizing, rotating, cutting, copying, etc...
  6. Wrappers for OpenCV canvas drawing features
      * Helper functions for drawing points, lines, polygons, text, etc...
  7. Example :mod:`~.helpers` module for basic face normalization.
      * Gives a basic re-implementation of ``dlib``'s ``get_face_chip()`` method.
