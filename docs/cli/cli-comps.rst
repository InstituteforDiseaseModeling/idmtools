.. _COMPS CLI:

=====
COMPS
=====

The COMPS platform related commands can be accessed with either ``idmtools comps`` or ``comps-cli``. All comps command require a target configuration block or alias to use to configure the connection to COMPS. See the details of the top level command below for detailed help:

.. command-output:: idmtools comps --help

You can login to a comps environment by using the ``idmtools comps CONFIG_BLOCK login`` command. See the help below:

.. command-output:: idmtools comps CONFIG_BLOCK login --help

You can assetize outputs from the CLI by running ``idmtools comps CONFIG_BLOCK assetize-outputs``:

.. command-output:: idmtools comps CONFIG_BLOCK assetize-outputs --help