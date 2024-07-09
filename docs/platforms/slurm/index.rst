=====
SLURM
=====
The |SLURM_s| platform allows use of the |SLURM_l|. "Slurm is an open source, fault-tolerant, and highly scalable cluster management and job scheduling system for large and small Linux clusters.", as quoted from (https://slurm.schedmd.com/overview.html). For high-level architecture information about |SLURM_s|,
see (https://slurm.schedmd.com/quickstart.html#arch).
For architecture and included packages information about |IT_s| and |SLURM_s|,
see (:doc:`../../reference`).


Prerequisites
=============
* Linux client


* |SLURM_s| cluster access and general understanding

* |Python_IT| (https://www.python.org/downloads/release)

* Python virtual environments

    Python virtual environments enable you to isolate your Python environments from one
    another and give you the option to run multiple versions of Python on the same computer. When using a
    virtual environment, you can indicate the version of Python you want to use and the packages you
    want to install, which will remain separate from other Python environments. You may use
    ``virtualenv``, which requires a separate installation, but ``venv`` is recommended and included with Python 3.7+.

Configuration
=============
The Slurm platform requires you to provide some configuration elements to define its operation.

You can define these parameters in your ``idmtools.ini`` file by adding a configuration block for Slurm.


  idmtools.ini example::

    [SLURM_LOCAL]
    type = SLURM
    job_directory = /home/userxyz/experiments


You can also do this directly from code by passing the minimum requirements
  Python script example::

    Platform('SLURM_LOCAL', job_directory='/home/userxyz/experiments')



Configuration Options
`````````````````````
.. list-table:: Title
   :header-rows: 1

   * - Parameter
     - Description
   * - **job_directory**
     - This defines the location that |IT_s| will use to manage experiments on the |SLURM_s| cluster. The directory should be located somewhere that is mounted on all |SLURM_s| nodes at the same location. If you are unsure, ask your |SLURM_s| server administrator for guidance.
   * - mode
     - Allows you to control the operational mode for |IT_s|. There are two modes currently supported.
       * - local
       * - bridged
       Bridged mode is *required* if you are running from within a Singularity container. See :ref:``Operation Modes`` for details.

.. note::

    Bold parameters are required

Operation Modes
===============

The |SLURM_s| platform supports two modes of operation, Local and Bridged. Local is the default mode.

Bridged
```````
Bridged mode allows you to utilize the emodpy/idmtools Singularity environment containers.
This is accomplished through a script that manages the communication to Slurm outside the container.

Bridged mode requires the package `idmtools-slurm-utils`.

To use bridged mode, before running your container you must run the bridge script outside the container::

    idmtools-slurm-bridge

If you plan on using the same terminal, you may want to run the bridge in the background::

    idmtools-slurm-bridge &

Once you have the bridge running, you can now run idmtools scripts from within Singularity containers. Ensure your platform is configured to use bridged mode::

    singularity exec idmtools_1.6.8 bash
    $ python my_script.py

Tips
....
When using the slurm-bridge, there are a few tips for use

1. When you background the process by running::

       idmtools-slurm-bridge &

   You will need to run::

       fg

   See [Foreground and Background Processes](https://www.linuxshelltips.com/foreground-and-background-process-in-linux/) in Linux

2. You may need to load modules before executing the bridge. See [Modules documentation](https://curc.readthedocs.io/en/latest/compute/modules.html) for more details.

Local
`````
Local operation is meant to be executed directly on a |SLURM_s| cluster node.


Recommendations
===============

* Simulation results and files should be backed up

Getting started
===============
After you have installed |IT_s| (:doc:`../../basic-installation` or :doc:`../../dev-installation`) and met the
above listed prerequisites, you can begin submitting and running jobs to your |SLURM_s| cluster with |IT_s|.
First verify your |SLURM_s| platform is running. Then submit a job with the included example Python script.

Verify |SLURM_s| platform is running
````````````````````````````````````
Type the following at a terminal session to verify that |SLURM_s| platform is running::

    sinfo -a

This will list your available partitions, and status. You should see output similar to the following::

    PARTITION AVAIL  TIMELIMIT  NODES  STATE NODELIST
    LocalQ*      up   infinite      1   idle localhost


Submit a job
````````````
Run the following included Python script to submit and run a job on your |SLURM_s| cluster::

    /examples/native_slurm/python_sims.py


.. note::

    ``workitems`` and ``AssetCollection`` are not supported on the |SLURM_s| platform with |IT_s|. If you've
    used the |COMPS_s| platform with |IT_s| you may have scripts using these objects. You would need
    to update these scripts without using these objects in order to run them on the |SLURM_s| platform.


.. toctree::
    :maxdepth: 2

    options
    cancel
    run-script-as-slurm-job