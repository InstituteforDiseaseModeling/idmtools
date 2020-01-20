from idmtools.analysis.analyze_manager import AnalyzeManager
import os
import pandas as pd
from idmtools.entities import IAnalyzer


class TagsAnalyzer(IAnalyzer):
    def __init__(self, uid=None, working_dir=None, parse=True):
        super().__init__(uid, working_dir, parse)
        self.exp_id = None

    def map(self, data, simulation):
        df = pd.DataFrame(columns=simulation.tags.keys())
        df.loc[str(simulation.uid)] = list(simulation.tags.values())
        df.index.name = 'SimId'
        return df

    def reduce(self, all_data):
        exp_id = str(next(iter(all_data.keys())).experiment.uid)
        results = pd.concat(list(all_data.values()), axis=0)
        os.makedirs(exp_id, exist_ok=True)
        results.to_csv(os.path.join(exp_id, 'tags.csv'))
