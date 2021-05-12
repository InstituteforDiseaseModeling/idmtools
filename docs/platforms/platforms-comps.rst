==============
COMPS platform
==============

The |COMPS_s| platform allows use of the |COMPS_s| HPC. |COMPS_s| has multiple environments. Most have predefined aliases that can be used
to quickly use the environments. Here are a list of predefined environments:

* BELEGOST
* BAYESIAN
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
   comps/add_2ac
   comps/assetize_output
   comps/download.rst
   comps/errors.rst
   comps/scheduling.rst
   comps/singularity_build.rst