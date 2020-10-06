System Requirements
===================

There are several required system requirements necessary for this package to work which
we unfortunately cannot bundle in this package.
The following sections will lead you through the installation of the necessary system
requirements.

`cmake <https://cmake.org/>`_
-----------------------------

This tool is necessary as `dlib <http://dlib.net/>`_ needs to be built upon install.

.. tabs::

   .. group-tab:: Linux

      Debian / Ubuntu

      .. code-block:: bash

         apt install cmake

   .. group-tab:: MacOS

      Homebrew

      .. code-block:: bash

         brew install cmake

      Macports

      .. code-block:: bash

         port install cmake

   .. group-tab:: Windows

      `Download the CMake installer <https://cmake.org/download/>`_ and make sure to
      enable the setting to "Add CMake to the system PATH for all users" when
      installing.
      You may need to restart your shell depending on what terminal emulator you are
      using in Windows.

      Make sure that you can run ``cmake --version`` in your shell without recieving a
      non-zero exit status code to verify your installation.

`libmagic <https://man7.org/linux/man-pages/man3/libmagic.3.html>`_
-------------------------------------------------------------------

This library helps us to determine the type of content we are attempting to process.
We need this to be able to optimally determine how to consume the data for an arbitrary
media file since OpenCV is pretty lacking in this area.

.. tabs::

   .. group-tab:: Linux

      Debian / Ubuntu

      .. code-block:: bash

         apt install libmagic1

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
