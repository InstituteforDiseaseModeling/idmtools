=====================
|DT| example analyzer
=====================

The following |DT| example performs analysis on simulation output data in .csv files and returns the result data in a .csv file::

    import os
    import pandas as pd
    from simtools.Analysis.BaseAnalyzers import BaseAnalyzer
    from simtools.Analysis.AnalyzeManager import AnalyzeManager
    from simtools.SetupParser import SetupParser


    class CSVAnalyzer(BaseAnalyzer):

        def __init__(self, filenames, parse=True):
            super().__init__(parse=parse, filenames=filenames)
            if not all(['csv' in os.path.splitext(f)[1].lower() for f in self.filenames]):
                raise Exception('Please ensure all filenames provided to CSVAnalyzer have a csv extension.')

        def initialize(self):
            if not os.path.exists(os.path.join(self.working_dir, "output_csv")):
                os.mkdir(os.path.join(self.working_dir, "output_csv"))

        def select_simulation_data(self, data, simulation):
            concatenated_df = pd.concat(list(data.values()), axis=0, ignore_index=True, sort=True)
            return concatenated_df

        def finalize(self, all_data: dict) -> dict:

            results = pd.concat(list(all_data.values()), axis=0,
                                keys=[str(k.id) for k in all_data.keys()],
                                names=['SimId'])
            results.index = results.index.droplevel(1)

            results.to_csv(os.path.join("output_csv", self.__class__.__name__ + '.csv'))


    if __name__ == "__main__":

        SetupParser.init(selected_block='HPC', setup_file="simtools.ini")
        filenames = ['output/c.csv']
        analyzers = [CSVAnalyzer(filenames=filenames)]
        manager = AnalyzeManager('9311af40-1337-ea11-a2be-f0921c167861', analyzers=analyzers)
        manager.analyze()