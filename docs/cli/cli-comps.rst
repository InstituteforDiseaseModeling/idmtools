.. _COMPS CLI:

=========
CLI COMPS
=========

The |COMPS_s| platform related commands can be accessed with either
``idmtools comps`` or ``comps-cli``. All comps command require a target configuration
block or alias to use to configure the connection to |COMPS_s|. See the details
of the top level command below for detailed help:

.. command-output:: idmtools comps --help
   :returncode: 0

You can login to a |COMPS_s| environment by using the ``idmtools comps CONFIG_BLOCK login``
command. See the help below:

.. command-output:: idmtools comps CONFIG_BLOCK login --help
   :returncode: 0

You can assetize outputs from the CLI by running ``idmtools comps CONFIG_BLOCK assetize-outputs``:

.. command-output:: idmtools comps CONFIG_BLOCK assetize-outputs --help
   :returncode: 0

You can download from the CLI by running ``idmtools comps CONFIG_BLOCK download``:

.. command-output:: idmtools comps CONFIG_BLOCK download --help
   :returncode: 0