DownloadWorkItem
================

:py:class:`~idmtools_platform_comps.utils.download.download.DownloadWorkItem` will let you
download files using glob patterns, and also from the CLI. You can download files from one or many experiments, simulations, work items, and asset collection.

Download uses glob patterns to select or deselect files. See
https://docs.python.org/3/library/glob.html for details on glob patterns.
The default configuration is set to download to all outputs, "**" pattern, and exclude the ".log", "StdOut.txt", "StdErr.txt", and "WorkOrder.json" files.

You can see a list of files that will be downloaded without downloading them by using the
**dry_run** parameter. The file list will be in the output of the work item or printed on the CLI.


Also review the class details :py:class:`~idmtools_platform_comps.utils.download.download.DownloadWorkItem`.

You can also run this command from the CLI. For details, see :ref:`COMPS CLI reference<CLI COMPS Platform>`

Download errors
---------------

See :ref:`COMPS Errors reference<COMPS Errors>`