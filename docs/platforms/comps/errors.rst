COMPS Errors
------------

The following errors mostly occur in SSMT workitems that run on |COMPS_s|:

* **NoFileFound** - This means the patterns you specified resulted in no files found. Review your patterns.
* **CrossEnvironmentFilterNotSupport** - This occurs when you attempt to filter an item in a |COMPS_s| environment that does not match that of the workitem. Use the same environment for your workitem as you did for your original item.
* **AtLeastOneItemToWatch** - You cannot run assetize without linking at least one item.
* **DuplicateAsset** - The resulting :term:`asset collection` would have duplicate assets. See the error for a list of duplicate assets. This often occurs when filtering either experiments or multiple items. With experiments, this can be avoided by using the *simulation_prefix_format_str* to place the assets into sub-folders. When processing multiple workitems with files that would overlap, you can use *work_item_prefix_format_str*. For other cases, you may need to do multiple runs and exclude patterns such as combining two asset collections with a single file that overlaps.