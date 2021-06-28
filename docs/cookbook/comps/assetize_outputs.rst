.. _Cookbook Assetize Outputs:

================
Assetize Outputs
================

For an overview of assetizing outputs, see :ref:`Assetize Outputs`.

Excluding files from assetizing
-------------------------------

Sometimes some of the files overlap with patterns you would like to include in a destination. In the following example, there are 100 files created with the *.out* extension. We would like all the files except "3.out" and "5.out". We can just add these two files to the exclude patterns of an :py:class:`~idmtools_platform_comps.utils.assetize_output.assetize_output.AssetizeOutput` object.

.. literalinclude:: ../../../examples/cookbook/comps/assetize_outputs/excluding_files/example.py
    :language: python

Using with experiments
----------------------

The following demonstrates assetizing the output of experiments. An important part to remember with experiments is that they typically have multiple simulations. To avoid conflicts in the assetized output, the default behaviour is to use the *simulation.id* as a folder name for each simulation output. We can include the original experiment asset collection in filtering as well by using the *include_assets* parameter.

.. literalinclude:: ../../../examples/cookbook/comps/assetize_outputs/experiment/example.py
    :language: python