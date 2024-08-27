Assetize outputs workitem
=========================

Assetizing outputs allows you to create an :py:class:`~idmtools.assets.asset_collection.AssetCollection`
from the outputs of a previous :py:class:`~idmtools.entities.experiment.Experiment`,
:py:class:`~idmtools.entities.simulation.Simulation`, workitem (:py:class:`GenericWorkItem<GenericWorkItem>`, :py:class:`~idmtools_platform_comps.ssmt_work_items.comps_workitems.SSMTWorkItem`,
:py:class:`~idmtools_platform_comps.utils.singularity_build.SingularityBuildWorkItem`) and other
asset collections. In addition, you can create assets from multiple items of these type.
For example, three simulations and an asset collection, or an experiment and a workitem.
:py:class:`~idmtools_platform_comps.utils.assetize_output.assetize_output.AssetizeOutput`
is implemented as a workitem that depends on other items to complete before running.

Assetized outputs are available on |COMPS_s| in the :term:`asset collection` for the
associated workitem.

Assetize outputs using glob patterns to select or deselect files. See
https://docs.python.org/3/library/glob.html for details on glob patterns.
The default configuration is set to assetize all outputs, "**" pattern, and exclude
the ".log", "StdOut.txt", "StdErr.txt", and "WorkOrder.json" files.

You can see a list of files that will be assetized without assetizing them by using the **dry_run** parameter. The file list will be in the output of the workitem.

See the :ref:`Cookbook <Assetize Outputs>` for examples of assetizing outputs.

Also review the class details :py:class:`~idmtools_platform_comps.utils.assetize_output.assetize_output.AssetizeOutput`

You can also run this command from the CLI. For details, see :ref:`COMPS CLI reference<CLI COMPS Platform>`.

Errors
------

See :ref:`COMPS Errors reference<COMPS Errors>`