.. _Assetize Outputs:

Assetize Outputs
================

Assetizing outputs allows you to create an Asset Collection from the outputs of a previous Experiment,
Simulation, Workitem and other Asset Collections. In Addition, you can create assets from multiple items of these type.
For examples, 3 simulations and an Asset Collection, or an experiment and a workItem. Assetize Outputs is implemented
as a workitem that depends on other items to complete before running.

AssetizeOutputs using glob patterns to select or deselect files. See https://docs.python.org/3/library/glob.html for details on glob patterns. The default configuration is set to Assetize all outputs, "**" pattern, and exclude the "StdOut.txt", "StdErr.txt", and "WorkOrder.json" files.

You can see a list of files that will be assetized without assetizing them by using the dry_run parameter. The file
list will be in the output of the work item.

See the :ref:`Cookbook <Cookbook Assetize Outputs>` for examples of Assetizing outputs

Also review the class details :class:`idmtools_platform_comps.utils.assetize_output.assetize_output.AssetizeOutput`

Errors
------

NoFileFound - This means the patterns you specified resulted in no files found. Review your patterns.