=====
SLURM
=====
The |SLURM_s| platform allows use of the |SLURM_l|. "Slurm is an open source, fault-tolerant, and highly scalable cluster management and job scheduling system for large and small Linux clusters.", as quoted from (https://slurm.schedmd.com/overview.html). For high-level architecture information about |SLURM_s|,
see (https://slurm.schedmd.com/quickstart.html#arch).
For architecure and included packages information about |IT_s| and |SLURM_s|,
see (:doc:`../reference`).


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
    ``virtualenv``, which requires a separate installation, but ``venv`` is recommended and included with Python 3.3+.

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
   * - job_directory
     - This defines the location that idmtools will use to manage experiments on the slurm cluster. The directory should be located somewhere that is mounted on all slurm nodes at the same location. If you are unsure, ask your Slurm Server Administrator for guidance.
   * - mode
     - Allows you to control the operational mode for idmtools. There are two modes currently supported.
       * - local
       * - bridged
       Bridged mode is *required* if you are running from within a singularity container. See :ref:``Operation Modes`` for details.


Operation Modes
===============

Local
`````

Bridged
```````

Recommendations
===============

* Simulation results and files should be backed up

* Specify where you want simulations, experiments, and suites written to. You can do this by either using the ``job_directory``
  option in the ``idmtools.ini`` file or you can specify the job directory within the Python script when you define the
  |SLURM_s| platform.

  idmtools.ini example::

    [SLURM_LOCAL]
    type = SLURM
    job_directory = /home/userxyz/experiments

  Python script example::

    Platform('SLURM_LOCAL', job_directory='/home/userxyz/experiments')

.. note::

    If you create a [SLURM_LOCAL] block within idmtools.ini and do not specify ``job_directory``,
    then |IT_s| will throw an exception error. If you do not specify ``job_directory`` in the Python script
    then |IT_s| defaults to the directory from which you ran the simulations.

Getting started
===============
After you have installed |IT_s| (:doc:`basic-installation` or :doc:`dev-installation`) and met the
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

    commands
    cancel