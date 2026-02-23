=================
Example analyzers
=================

You can use the following example analyzers as templates to get started using |IT_s|:

| :py:class:`~idmtools.analysis.add_analyzer.AddAnalyzer`
| :py:class:`~idmtools.analysis.csv_analyzer.CSVAnalyzer`
| :py:class:`~idmtools.analysis.download_analyzer.DownloadAnalyzer`
| :py:class:`~idmtools.analysis.tags_analyzer.TagsAnalyzer`

Each example analyzer is configured to run with existing simulation data and already configured options, such as using the |COMPS_s| platform and existing experiments. This allows you to easily run these example analyzers for demonstrating some of the tasks you may want to accomplish when analyzing simulation output data. You can then use and modify these examples for your specific needs.

.. include:: /reuse/comps_note.txt

For a description of each of these analyzers please see the following:

* :py:class:`~idmtools.analysis.add_analyzer.AddAnalyzer`: Gets metadata from simulations, maps to key:value pairs, and returns a .txt output file.
* :py:class:`~idmtools.analysis.csv_analyzer.CSVAnalyzer`: Analyzes .csv output files from simulations and returns a .csv output file.
* :py:class:`~idmtools.analysis.download_analyzer.DownloadAnalyzer`: Downloads simulation output files for analysis on local computer resources.
* :py:class:`~idmtools.analysis.tags_analyzer.TagsAnalyzer`: Analyzes tags from simulations and returns a .csv output file.

Each of the included example analyzers inherit from the built-in analyzers and the :py:class:`~idmtools.entities.ianalyzer.IAnalyzer` abstract class:

.. image:: /diagrams/ianalyzer-exampleanalyzers.png
   :alt: Analyzer Examples
   :align: center

For more information about the built-in analyzers, see :doc:`analyzers-create`. There are also additional examples, such as forcing analyzers to use a specific working directory and how to perform partial analysis on only succeeded or failed simulations:

.. toctree::

   analyzers-forcedir
   analyzers-partial