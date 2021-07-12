========================
|DT| converted to |IT_s|
========================

The following converted from |DT| to |IT_s| example performs analysis on simulation output data in .csv files and returns the result data in a .csv file::

    import os
    import pandas as pd
    from idmtools.entities import IAnalyzer
    from idmtools.analysis.analyze_manager import AnalyzeManager
    from idmtools.core import ItemType
    from idmtools.core.platform_factory import Platform


    class CSVAnalyzer(IAnalyzer):

        def __init__(self, filenames, parse=True):
            super().__init__(parse=parse, filenames=filenames)
            if not all(['csv' in os.path.splitext(f)[1].lower() for f in self.filenames]):
                raise Exception('Please ensure all filenames provided to CSVAnalyzer have a csv extension.')

        def initialize(self):
            if not os.path.exists(os.path.join(self.working_dir, "output_csv")):
                os.mkdir(os.path.join(self.working_dir, "output_csv"))

        def map(self, data, simulation):
            concatenated_df = pd.concat(list(data.values()), axis=0, ignore_index=True, sort=True)
            return concatenated_df

        def reduce(self, all_data):

            results = pd.concat(list(all_data.values()), axis=0,
                                keys=[k.id for k in all_data.keys()],
                                names=['SimId'])
            results.index = results.index.droplevel(1)

            results.to_csv(os.path.join("output_csv", self.__class__.__name__ + '.csv'))
        
        
    if __name__ == '__main__':

        platform = Platform('COMPS')
        filenames = ['output/c.csv']    
        analyzers = [CSVAnalyzer(filenames=filenames)]
        experiment_id = '9311af40-1337-ea11-a2be-f0921c167861' 
        manager = AnalyzeManager(configuration={}, partial_analyze_ok=True, platform=platform,
                                 ids=[(experiment_id, ItemType.EXPERIMENT)],
                                 analyzers=analyzers)
        manager.analyze()

You can quickly see this analyzer in use by running the included :py:class:`~idmtools.analysis.csv_analyzer.CSVAnalyzer` example class.