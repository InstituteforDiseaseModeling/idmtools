=======
Install
=======

You can install |IT_s| in two different ways. If you intend to use |IT_s| as
|IDM_s| builds it, follow the instructions in :doc:`basic-installation`.
However, if you intend to modify the |IT_s| source code to add new
functionality, follow the instructions in :doc:`dev-installation`. Whichever
installation method you choose, the prerequisites are the same.

.. _idmtools-prereqs:

Prerequisites
=============

* Windows 10 Pro or Enterprise, or a Linux operating system
* |Python_IT| (https://www.python.org/downloads/release)
* Python virtual environments (https://docs.python.org/3/library/venv.html)

* Docker (https://docs.docker.com/)

  On Windows, please use Docker Desktop 4.0.0 or later

.. note::

  Docker is optional for the basic installation of |IT_s|; it is only required for running simulations or analyses locally with the ``ContainerPlatform``.

.. toctree::

    basic-installation
    dev-installation