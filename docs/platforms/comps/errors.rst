.. _COMPS_Errors:

Errors
------

These errors mostly cover errors that happen in SSMT WorkItems that run on COMPS currently.

NoFileFound - This means the patterns you specified resulted in no files found. Review your patterns.
CrossEnvironmentFilterNotSupport - This occurs when you attempt to filter an item in a COMPS environment that does not match that of the workitem. Use the same environment for your workitem as you did for your original item
AtLeastOneItemToWatch - You cannot run assetize without linking at least one item
DuplicateAsset - The resulting asset collection would have duplicate assets. See the error for a list of duplicate assets. This often occurs when filtering either Experiments or multiple items.
With Experiments, this can be avoided by using the *simulation_prefix_format_str* to place the assets into sub-folders. When processing multiple work items with files that would overlap,
you can use *work_item_prefix_format_str*. For other cases, you may need to do multiple runs and exclude patterns such as combining two AssetCollections with a single file that overlaps.