.. _getting-started:

===============
Getting Started
===============

| **Welcome to Facelift!**
| This page should hopefully provide you with enough information to get you started detecting and recognizing faces.

Installation and Setup
======================

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


System Requirements
~~~~~~~~~~~~~~~~~~~

There are several required system requirements necessary for this package to work which
we unfortunately cannot bundle in this package.
The following sections will lead you through the installation of the necessary system
requirements.

``libmagic``
------------

This library helps us to determine the type of content we are attempting to process.
We need this to be able to optimally determine how to consume the data for an arbitrary
media file since opencv is pretty lacking in this area.

.. tabs::

   .. group-tab:: Linux

      Debian / Ubuntu

      .. code-block:: bash

         apt install libmagic1

      Arch

      .. code-block:: bash

         pacman -S file

      CentOS

      .. code-block:: bash

         yum install file-devel

   .. group-tab:: MacOS

      Homebrew

      .. code-block:: bash

         brew install libmagic

      Macports

      .. code-block:: bash

         port install file

   .. group-tab:: Windows

      We install `python-magic-bin <https://pypi.org/project/python-magic-bin/>`_
      as a dependency if you are installing from a Windows environment.
      This package **should** contain working binaries for ``libmagic`` built for
      Windows.
      If you encounter unhandled errors using ``libmagic`` on Windows, please `create an
      issue <https://github.com/stephen-bunn/facelift/issues>`_ to let us know what you
      are experiencing.
