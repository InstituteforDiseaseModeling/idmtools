import os
import pandas as pd
from idmtools.entities import IAnalyzer
from idmtools.core import EntityStatus


class CSVAnalyzer(IAnalyzer):
    def __init__(self, filenames, parse=True):
        super().__init__(parse, filenames=filenames)
        if not all(['csv' in os.path.splitext(f)[1].lower() for f in self.filenames]):
            raise Exception('Please ensure all filenames provided to CSVAnalyzer have a csv extension.')

    def map(self, data, simulation):

        concatenated_df = pd.concat(list(data.values()), axis=0, ignore_index=True, sort=True)
        return concatenated_df

    def reduce(self, all_data):

        # Let's hope the first simulation is representative
        first_sim = next(iter(all_data.keys()))
        exp_id = str(first_sim.experiment.uid)

        results = pd.concat(list(all_data.values()), axis=0,
                            keys=[str(k.uid) for k in all_data.keys()],
                            names=['SimId'])
        results.index = results.index.droplevel(1)  # Remove default index

        os.makedirs(exp_id, exist_ok=True)
        # NOTE: If running twice with different filename, the output files will collide
        results.to_csv(os.path.join(exp_id, self.__class__.__name__+'.csv'))


