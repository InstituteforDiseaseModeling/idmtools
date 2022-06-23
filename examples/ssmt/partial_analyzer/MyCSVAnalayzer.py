import os
from typing import Dict

import pandas as pd

from idmtools.entities import IAnalyzer


class MyCSVAnalyzer(IAnalyzer):
    def __init__(self, filenames, output_path="output"):
        super().__init__(filenames=filenames)
        self.output_path = output_path

    def initialize(self):
        self.output_path = os.path.join(self.working_dir, self.output_path)
        os.makedirs(self.output_path, exist_ok=True)

    def map(self, data, simulation) -> pd.DataFrame:
        selected_df = pd.concat(list(data.values()), axis=0, ignore_index=True, sort=True)
        return selected_df

    def reduce(self, all_data: Dict):
        results = pd.concat(list(all_data.values()), axis=0,
                            keys=[str(k.uid) for k in all_data.keys()],
                            names=['SimId'])
        results.index = results.index.droplevel(1)

        # Make a directory labeled the exp id to write the csv results to
        first_sim = list(all_data.keys())[0]
        exp_id = first_sim.experiment.id
        output_folder = os.path.join(self.output_path, exp_id)
        os.makedirs(output_folder, exist_ok=True)
        results.to_csv(os.path.join(output_folder, self.__class__.__name__ + '.csv'))