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
If you find that you are building OpenCV_ on installation, it's likely that you are
installing an old version from ``pythonhosted.org`` which does **not** include prebuilt
binaries.
This will likely cause many issues with OpenCV_ not being built with proper support for
GTK X11 support which is necessary for reading media and opening windows.
If you run into this, try updating your local ``pip`` to the newest version (which
should install the dependency from PyPi).
Note that this dependency doesn't come prebuilt with any GPU support.

The ``dlib`` dependency will always need to be built when installing ``facelift``.
This requires that ``cmake`` is available on the system and doesn't build with any GPU
support.


.. _model-installation:

Model Installation
==================

Due to PyPi's upload limits, we cannot bundle the associated landmark and ResNet models
for face detection or face encoding.
Similar to how other projects have dealt with this issue in the past, we have supplied a
special module :mod:`~._data` to programmatically fetch the necessary pre-trained models
for using this package.

The :func:`~._data.download_data` function will attempt to fetch the models uploaded to
the latest GitHub release.

.. code-block:: python

   from facelift._data import download_data
   download_data()


If for some reason we mess up and forget to upload the models to the GitHub release, you
can manually specify the release tag using the ``release_tag`` parameter.
This will attempt to fetch the models from a very release instead of the very latest.

.. code-block:: python

   from facelift._data import download_data
   download_data(release_tag="v0.1.0")


You can also see the basic download status written out to ``stdout`` by setting the
``display_progress`` parameter to ``True``.

.. code-block:: python

   from facelift._data import download_data
   download_data(display_progress=True)


I would prefer to be able to bundle the models along with the package since we are
building a project revolving around **very specific** feature models and frameworks
(rather than providing an open-ended framework for face detection).
However, this is just something we need to do to satisfy PyPi.

.. important::
   At the moment, the downloaded models will be placed in a ``data`` directory within
   the ``facelift`` package.
   This means that your system or virtual environment will contain the downloaded
   models.
   If you are interested in the absolute path that the downloaded models are being
   written to, you should set the ``display_progress`` flag to ``True`` as we write out
   where files are being stored.

.. include:: ./gpu-support.rst
