.. _Bug Report:
   https://github.com/stephen-bunn/facelift/issues/new?labels=bug&template=bug-report.md

.. _getting-started:

===============
Getting Started
===============

| **Welcome to Facelift!**
| This page should hopefully provide you with enough information to get the ``facelift``
  package installed so you can start detecting face features.
  If you run into any issues with installation, please create a `Bug Report`_
  with details about your current operating system and package version and we can try to
  improve our setup documentation.


.. _system-requirements:
.. include:: system-requirements.rst


Package Installation
====================

Installing the package should be super duper simple as we utilize Python's setuptools.

.. code-block:: bash

   $ poetry add facelift
   $ # or if you're old school...
   $ pip install facelift

Or you can build and install the package from the git repo.

.. code-block:: bash

   $ git clone https://github.com/stephen-bunn/facelift.git
   $ cd ./facelift
   $ python setup.py install


Installing ``opencv-python`` *should* be quick for many environments as prebuilt
packages are provided from PyPi.
If you find that you are building OpenCV on installation, it's likely that you are
installing an old version from ``pythonhosted.org`` which does **not** include prebuilt
binaries.
This will likely cause many issues with OpenCV not being built with proper support for
GTK X11 support which is necessary for reading media and opening windows.
If you run into this, try updating your local ``pip`` to the newest version (which
should install the dependency from PyPi).
Note that this dependency doesn't come prebuilt with any GPU support.

The ``dlib`` dependency will always need to be built when installing ``facelift``.
This requires that ``cmake`` is available on the system and doesn't build with any GPU
support.

.. note::
   The size of the package is fairly large at ~90MB unpacked.
   Since we bundle the ``dlib`` and ``resnet`` models along with the release, most of
   what you are downloading are actually just trained models for face detection and
   recognition.

   Currently, we don't have the method for avoiding this installation as the core
   functionality of the package depends on these models existing and being declared and
   loaded in a specific way.
   I have several ideas on how to separate the data from the code.
   However, this isn't a huge concern to me for a ``v1.0.0`` release.


.. include:: ./gpu-support.rst
