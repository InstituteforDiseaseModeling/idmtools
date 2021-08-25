============
SSMT Recipes
============


Run Analysis Remotely(Platform Analysis)
----------------------------------------

The following example demonstrates using the PlatformAnalysis object to run AnalyzerManager server-side. Running on the
server side has the advantage of not needing to download the files required for analysis, as well as additional computational power.

In this example, we are going to run the following analyzers

.. literalinclude:: ../../../examples/ssmt/simple_analysis/analyzers/AdultVectorsAnalyzer.py
    :language: python

.. literalinclude:: ../../../examples/ssmt/simple_analysis/analyzers/PopulationAnalyzer.py
    :language: python

.. literalinclude:: ../../../examples/ssmt/simple_analysis/run_ssmt_analysis.py
    :language: python

See :py:class:`idmtools.analysis.platform_anaylsis.PlatformAnalysis`.
