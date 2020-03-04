import os
import pandas as pd
import ast
from logging import getLogger

from idmtools.core.platform_factory import Platform
from idmtools.entities.ianalyzer import IAnalyzer

logger = getLogger(__name__)

# This tags analyzer is for test_sweep_* test cases with a, b, c tags and params


class SimFilterAnalyzerById(IAnalyzer):
    data_group_names = ['sim_id', 'key', 'value']

    def __init__(self, filenames=None, output_path=None, **kwargs):
        super().__init__(filenames=filenames, parse=False, **kwargs)
        self.output_path = output_path or "output"
        self.p = Platform('COMPS2')

    def initialize(self):
        self.output_path = os.path.join(self.working_dir, self.output_path)
        os.makedirs(self.output_path, exist_ok=True)

    def get_sim_folder(self, item):
        """
        Concatenate the specified top-level output folder with the simulation ID.

        Args:
            item: A simulation output parsing thread.

        Returns:
            The name of the folder to download this simulation's output to.
        """
        return os.path.join(self.output_path, str(item.uid))

    def default_group_fn(self, k, v):
        return k

    def filter(self, simulation):
        return simulation.id != 'e6f2b1dc-7053-ea11-a2bf-f0921c167862'

    def map(self, data, simulation):
        df = pd.DataFrame(columns=simulation.tags.keys())  # Create a dataframe with the simulation tag keys
        df.loc[str(simulation.uid)] = list(simulation.tags.values())  # Get a list of the sim tag values
        df.index.name = 'SimId'  # Label the index keys you create with the names option

        match_results_dict = {}
        results = data[self.filenames[0]]
        results_dict = ast.literal_eval(results.decode('utf-8'))
        for key, value in results_dict.items():
            if key == "b":
                match_results_dict[key] = value

        s = df.ix[:, 1].map(match_results_dict)
        lens = s.astype(str).str.len()
        match_results_df = pd.DataFrame({
            'key': df['b'].keys,
            'value': df['b'].values.repeat(lens)

        })
        print(match_results_df)
        return match_results_df

    def reduce(self, all_data):
        b_result_list = []

        for sim, sim_data in all_data.items():
            b_result_list.append(sim_data)

        b_results_df = pd.DataFrame.from_records(b_result_list, columns=['SimId', 'key', 'value'])
        b_results_df.to_csv(os.path.join("output", 'b_match.csv'),
                            index_label='index')  # Write the matched sim results to a csv
