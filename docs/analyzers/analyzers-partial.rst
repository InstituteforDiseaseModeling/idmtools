================
Partial analysis
================

You can use analyzers for a partial analysis of simulations. This allows you to
only analyze succeeded simulations, while one or more simulations within an
experiment may have failed. In addition, you can analyze both succeeded and
failed simulations.

Analysis on only succeeded simulations
--------------------------------------

For partial analysis only on the succeeded simulations, where one or more
simulations may have failed, you set to "True" the **partial_analyze_ok**
parameter from the :py:class:`~idmtools.analysis.analyze_manager.AnalyzeManager`
class, as seen in the following python code excerpt::

        analyzers = [CSVAnalyzer(filenames=filenames)]
        manager = AnalyzeManager(platform=self.platform, partial_analyze_ok=True,
                                 ids=[(experiment_id, ItemType.EXPERIMENT)],
                                 analyzers=analyzers)
        manager.analyze()

Analysis on both succeeded and failed simulations
-------------------------------------------------

For analysis on both succeeded and failed simulations, you set to "True" the
**analyze_failed_items** parameter from the :py:class:`~idmtools.analysis.analyze_manager.AnalyzeManager` class, as seen in the following python code excerpt::

        analyzers = [CSVAnalyzer(filenames=filenames)]
        manager = AnalyzeManager(platform=self.platform, analyze_failed_items=True,                                 
                                 ids=[(experiment_id, ItemType.EXPERIMENT)],
                                 analyzers=analyzers)
        manager.analyze()