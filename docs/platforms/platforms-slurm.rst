=====
SLURM
=====
The |SLURM_s| platform allows use of the |SLURM_l|. "Slurm is an open source, fault-tolerant, and highly scalable cluster management and job scheduling system for large and small Linux clusters.", as quoted from (https://slurm.schedmd.com/overview.html). For high-level architecture information about |SLURM_s|, 
see (https://slurm.schedmd.com/quickstart.html#arch). 
For architecure and included packages information about |IT_s| and |SLURM_s|, 
see (https://docs.idmod.org/projects/idmtools/en/latest/reference.html).

.. :doc:`reference` errors out as unknown document when building sphinx local files, not sure why as the file exists and is in the same directory as other working referenced files, such as basis-installation...

Prerequisites
=============
* Linux client

* |SLURM_s| cluster access and general understanding of

* |Python_IT| (https://www.python.org/downloads/release)

* Python virtual environments

    Python virtual environments enable you to isolate your Python environments from one
    another and give you the option to run multiple versions of Python on the same computer. When using a
    virtual environment, you can indicate the version of Python you want to use and the packages you
    want to install, which will remain separate from other Python environments. You may use
    ``virtualenv``, which requires a separate installation, but ``venv`` is recommended and included with Python 3.3+.

Recommendations
````````````````
* sim_root should be a shared drive and mounted on all nodes in the cluster

* Simulation results and files should be backed up

Getting started
===============
After you have installed |IT_s| (:doc:`basic-installation` or :doc:`dev-installation`) and met the 
above listed prerequisites, you can begin submitting and running jobs to your |SLURM_s| cluster with |IT_s|. 
First verify your |SLURM_s| platform is running. Then submit a job with the included example Python script.

Verify |SLURM_s| platform is running
````````````````````````````````````
Type the following at a command prompt to verify that |SLURM_s| platform is running::

    add simple ping/hello-world script here

You should see the following output...::

    add return value/output from hello-world script

Submit a job
````````````
Run the following included Python script to submit and run a job on your |SLURM_s| cluster::

    simple python script name goes here

Upon completion you should see the following output...::

    return value/output from python script example

.. note::

        ``workitems`` are not supported on the |SLURM_s| platform with |IT_s|. If you've 
        used the |COMPS_s| platform with |IT_s| you may have scripts using this object. 
        To modify these scripts you should....


.. toctree::

    slurm/commands
    slurm/cancel
   