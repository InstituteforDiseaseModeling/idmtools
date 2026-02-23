=============================
Using analyzers with |SSMT_s|
=============================

If you have access to |COMPS_s|, you can use |IT_s| to run analyzers on |SSMT_l|. |SSMT_s| is integrated with |COMPS_s|, allowing you to leverage the HPC compute power for running both the analyzers and any pre or post processing scripts that you may have previously ran locally.

The :py:class:`~idmtools.analysis.platform_anaylsis.PlatformAnalysis` class is used for sending the needed information (such as analyzers, files, and experiment ids) as a |SSMT_s| work item to be run with |SSMT_s| and |COMPS_s|.

The following example, run_ssmt_analysis.py, shows how to use :py:class:`~idmtools.analysis.platform_anaylsis.PlatformAnalysis` for running analysis on |SSMT_s|:

    .. literalinclude:: ../../examples/ssmt/simple_analysis/run_ssmt_analysis.py

In this example two analyzers are run on an existing experiment with the output results saved to an output directory. After you run the example you can see the results by using the returned SSMTWorkItem id and searching for it under **Work Items** in |COMPS_s|.

.. include:: /reuse/comps_note.txt