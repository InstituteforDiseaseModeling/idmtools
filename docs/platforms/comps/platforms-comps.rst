.. _COMPS Platform:

==============
COMPS Platform
==============

The |COMPS_s| platform allows use of the |COMPS_s| HPC. |COMPS_s| has multiple environments. Most have predefined aliases that can be used
to quickly use the environments. Here are a list of predefined environments:

* SLURMSTAGE
* CALCULON
* SLURM
* SLURM2
* BOXY

You can also see a list of aliases and configuration options using the CLI command ``idmtools info plugins platform-aliases``

.. command-output:: idmtools info plugins platform-aliases

Utilities Unique to COMPS
-------------------------

.. toctree::
   options
   add_2ac
   assetize_output
   download.rst
   errors.rst
   scheduling.rst
   singularity_build.rst