=================
Example analyzers
=================

You can use the following example analyzers as templates to get started using |IT_s|: 

| :py:class:`idmtools.examples.analyzers.example_analysis_AddAnalyzer`
| :py:class:`idmtools.examples.analyzers.example_analysis_CSVAnalyzer`
| :py:class:`idmtools.examples.analyzers.example_analysis_DownloadAnalyzer`
| :py:class:`idmtools.examples.analyzers.example_analysis_EndpointsAnalyzer`
| :py:class:`idmtools.examples.analyzers.example_analysis_MultiCSVAnalyzer`
| :py:class:`idmtools.examples.analyzers.example_analysis_multiple_cases`
| :py:class:`idmtools.examples.analyzers.example_analysis_TagsAnalyzer`

Each example analyzer is configured to run with existing simulation data and already configured options, such as using the COMPS platform and existing experiments. This allows you to easily run these example analyzers for demonstrating some of the tasks you may want to accomplish when analyzing simulation output data. You can then use and modify these examples for your specific needs. For a description of each of these analyzers please see the following:

| **AddAnalyzer**: Gets metadata from simulations, maps to key:value pairs, and returns a .txt output file.

| **CSVAnalyzer**: Analyzes .csv output files from simulations and returns a .csv output file. 

| **DownloadAnalyzer**: Downloads simulation output files for analysis on local computer resources.

| **EndpointsAnalyzer**: Analyzes specified channels from InsetChart.json output files from simulations and returns a .csv output file.

| **MultiCSVAnalyzer**: Analyzes multiple .csv output files from simulations and returns a .csv output file.

| **multiple_cases**: Analyzes different output file types from simulations using multiple analyzers and prints results.

| **TagsAnalyzer**: Analyzes tags from simulations and returns a .csv output file.

Each of the included example analyzers inherit from the built-in analyzers and the :py:class:`~idmtools.entities.ianalyzer.IAnalyzer` abstract class:

.. uml::

    @startuml
    abstract class IAnalyzer        
    IAnalyzer <|-- BuiltinAnalyzers
    BuiltinAnalyzers <|-- ExampleAnalyzers  
    @enduml

For more information about the built-in analyzers, see :doc:`analyzers-create`.

.. toctree::

   analyzers-additems
   analyzers-forcedir
   analyzers-partial
