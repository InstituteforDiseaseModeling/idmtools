.. _Add 2AC:

Add to asset collection
=======================

|IT_s| allows you to add files, such as input and model libraries, to an :term:`asset collection` 
on |COMPS_s|. This allows you access and use these files when running model simulations on 
the |COMPS_s| platform.

Add files
---------

Files can be added specifically or by adding one or more directories to an asset collection.

Add specific files
^^^^^^^^^^^^^^^^^^

To add specific files to an asset collection you can use the 
:py:meth:`~idmtools.assets.asset_collection.AssetCollection.add_asset` 
or :py:meth:`~idmtools.assets.asset_collection.AssetCollection.add_assets` 
methods in the :py:class:`~idmtools.assets.asset_collection.AssetCollection` class. 

The following example shows how to add a Linux command-line shell file `file_name.sh` 
from the directory `inputs`, which is a local directory relative to the root 
of the model project files, and then add it to the experiment object::

    experiment.add_asset (os.path.join("inputs", "file_name.sh"))

Add directories
^^^^^^^^^^^^^^^

To add directories to an asset collection you can use 
the :py:meth:`~idmtools.assets.asset_collection.AssetCollection.add_directory` method in 
the :py:class:`~idmtools.assets.asset_collection.AssetCollection` class, 
as shown in the following example::

    experiment.assets.add_directory(assets_directory=os.path.join("yourlocaldir1", "youlocaldir2"))

Add libraries
-------------

To add a specific library to an asset collection you first add the libary package name to a 
requirements file, either lib_requirements_linux.txt or lib_requirements_wins.txt, and place 
the file in the root directory containing your model files. Then you 
use the ``add_libs_utils.py`` script to add the libary to the asset collection on |COMPS_s|.

Add to requirements file
^^^^^^^^^^^^^^^^^^^^^^^^

The following contains contents of an example requirements file::

    dbfread~=2.0.7
    PyCRS~=1.0.2
    ete3~=3.1.1
    czml~=0.3.3
    pygeoif~=0.7
    pyshp~=2.1.0
    rasterio~=1.1.5    
    matplotlib~=3.3.4
    pandas~=1.2.3
    h5py~=2.10.0

Upload library to asset collection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After including the desired libraries in the requirement file, you use the following 
Python script ``add_libs_utils.py`` to upload them to your asset collection::

    from idmtools.core.platform_factory import Platform
    from idmtools_platform_comps.utils.python_requirements_ac.requirements_to_asset_collection import \
        RequirementsToAssetCollection

    def main():
        #platform = Platform('COMPS2')
        platform = Platform('SLURM')

        env = platform.environment
        if env == 'Belegost' or env == 'Bayesian':  # COMPS or COMPS2
            pl = RequirementsToAssetCollection(platform, requirements_path='lib_requirements_wins.txt',
                                               local_wheels=['GDAL-3.1.2-cp36-cp36m-win_amd64.whl',
                                               'rasterio-1.1.5-cp36-cp36m-win_amd64.whl',
                                               'PyQt4-4.11.4-cp36-cp36m-win_amd64.whl'])
        else:  # SLURM env
            pl = RequirementsToAssetCollection(platform, requirements_path='lib_requirements_linux.txt',
                                               local_wheels=['GDAL-3.1.2-cp36-cp36m-manylinux1_x86_64.whl'])

        ac_id = pl.run(rerun=False) # only change to True if you want to regenerate same set of ac again
        print('ac_id: ', ac_id)
        with open(env + '_asset_collection.txt', 'w') as fn:
            fn.write(str(ac_id))

    if __name__ == '__main__':
        main()