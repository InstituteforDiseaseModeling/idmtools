.. _Cookbook Assetize Outputs:

================
Assetize Outputs
================

For overview of AssetizeOutputs, see :ref:`Assetize Outputs`

Excluding files from Assetizing
--------------------------------------------

Sometimes some of the files overlap with patterns you would like to include in a destination. In the below example, there are 100 files created with the *.out* extension. We would like all the files except 3.out and 5.out. We can just add those files to the exclude patterns. This example also demos how to use the *simulation_prefix_format_str* when we have only one simulation.

.. literalinclude:: ../../../examples/cookbook/comps/assetize_outputs/excluding_files/example.py
    :language: python

Using with experiments
----------------------

Simple demo that demos assetizing the output of experiments. The important part to remember with Experiments is normally they have multiple simulations. To avoid conflicts in the assetize output, the default behaviour is to use the *simulation.id* as a folder name for each simulation output. We can include the original experiment asset collection in filtering as well by using the *include_assets* parameter.

.. literalinclude:: ../../../examples/cookbook/comps/assetize_outputs/experiment/example.py
    :language: python
