================
Partial analysis
================

You can use analyzers for a partial analysis of simulations. For example, if you've run an experiment where one or more simulations failed then you can use analyzers with |IT_s| to only perform analysis on the succeeded simulations.

For partial analysis, you set to **True** the **partial_analyze_ok** parameter from the :py:class:`~idmtools.analysis.analyze_manager.AnalyzeManager` class, as seen in the following python code excerpt::

    analyzers = [CSVAnalyzer(filenames=filenames)]



        manager = AnalyzeManager(platform=self.platform, partial_analyze_ok=True,

                                 ids=[(experiment_id, ItemType.EXPERIMENT)],

                                 analyzers=analyzers)

        manager.analyze()