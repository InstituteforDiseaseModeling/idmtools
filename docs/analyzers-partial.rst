================
Partial analysis
================

You can use analyzers for a partial analysis of simulations. This includes the ability to only analyze succeeded simulations or to only analyze failed simulations.

Analysis on succeeded simulations
---------------------------------

For partial analysis only on the succeeded simulations, where one or more simulations may have failed, you set to **True** the **partial_analyze_ok** parameter from the :py:class:`~idmtools.analysis.analyze_manager.AnalyzeManager` class, as seen in the following python code excerpt::

        analyzers = [CSVAnalyzer(filenames=filenames)]
        manager = AnalyzeManager(platform=self.platform, partial_analyze_ok=True,
                                 ids=[(experiment_id, ItemType.EXPERIMENT)],
                                 analyzers=analyzers)
        manager.analyze()

Analysis on failed simulations
------------------------------

For partial analysis only on the failed simulations, you set to **True** the **analyze_failed_items** from the :py:class:`~idmtools.analysis.analyze_manager.AnalyzeManager` class, as seen in the following python code excerpt::

        analyzers = [CSVAnalyzer(filenames=filenames)]
        manager = AnalyzeManager(platform=self.platform, analyze_failed_items=True,
                                 ids=[(experiment_id, ItemType.EXPERIMENT)],
                                 analyzers=analyzers)
        manager.analyze()
