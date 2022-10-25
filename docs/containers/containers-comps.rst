=============================
Using containers in |COMPS_s|
=============================

You can use the Singularity container files (.sif) for running simulations 
on |COMPS_s|.

Run a job in COMPS with Singularity
===================================

|IT_s| includes examples to help you get up and running with Singularity on |COMPS_s|. 
First, you can run the `create_ubuntu_sif.py` script, located in 
examples/singularity/ubuntu-20-04/create_ubuntu_sif.py. This script creates an Ubuntu 
Singularity container based on the included definition file, `ubuntu_20_04_base.def`, 
and writes it to an asset collection on |COMPS_s|.

.. code-block:: python

    if __name__ == '__main__':
    platform = Platform("CALCULON")
    sbi = SingularityBuildWorkItem(name="Create ubuntu sif with def file", definition_file="ubuntu_20_04_base.def", image_name="ubuntu.sif")
    sbi.tags = dict(ubuntu="20.04")
    sbi.run(wait_until_done=True, platform=platform)
    if sbi.succeeded:
        # Write ID file
        sbi.asset_collection.to_id_file("ubuntu.id")

Once you have the required Linux .sif container file, you can then add your modeling 
files. For example, `create_covasim_sif.py`, located in 
examples/singularity/covasim/create_covasim_sif.py, uses the pre-created ubuntu 
container and associated asset collection id to create a new .sif container file 
for running simulations using Covasim.

.. code-block:: python

    if __name__ == '__main__':
    platform = Platform("CALCULON")
    sbi = SingularityBuildWorkItem(name="Create covasim sif with def file", definition_file="covasim_req.def", image_name="covasim_ubuntu.sif")
    # Try to load the ubuntu image from an id file
    pwd = PurePath(__file__).parent
    ub_base = pwd.joinpath("..", "ubuntu-20-04")
    fp = pwd.joinpath("ubuntu.id")
    sbi.add_assets(AssetCollection.from_id_file(fp))
    sbi.tags = dict(covasim=None)
    sbi.run(wait_until_done=True, platform=platform)
    if sbi.succeeded:
        sbi.asset_collection.to_id_file("covasim.id")

As the following example script, `run_covasim_sweep.py`, shows you can run simulations 
in a Singularity container on |COMPS_s| using the previously created .sif container file.

.. literalinclude:: ../../examples/singularity/covasim/run_covasim_sweep.py
    :language: python


.. (Lauren)

.. Examples
.. ========
.. The following examples of using containers in |COMPS_s| are included:

.. * Python
.. * R

.. Python example
.. --------------
.. (Clinton/Sharon) - should build off container build example to run using that container 

.. R example
.. ---------
.. (Lauren/Sharon) - should build off container build example to run using that container 

.. Singularity wrapper
.. ===================
.. (Clinton)
