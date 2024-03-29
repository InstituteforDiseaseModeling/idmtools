import os
import pandas as pd
import ast
from logging import getLogger
from idmtools.entities.ianalyzer import IAnalyzer

logger = getLogger(__name__)

# This tags analyzer is for test_sweep_* test cases with a, b, c tags and params


class SimFilterAnalyzer(IAnalyzer):

    def __init__(self, filenames=None, output_path="output", **kwargs):
        super().__init__(filenames=filenames, parse=False, **kwargs)
        self.output_path = output_path

    def initialize(self):
        self.output_path = os.path.join(self.working_dir, self.output_path)

        # Create the output path
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

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
        return int(simulation.tags.get("b")) == 2

    def map(self, data, simulation):
        results = data[self.filenames[0]]
        results_dict = ast.literal_eval(results.decode('utf-8'))
        for key, value in results_dict.items():
            if key == "b":
                return key, value

    def reduce(self, all_data):
        first_sim = list(all_data.keys())[0]  # get first Simulation
        exp_id = first_sim.experiment.id  # Set the exp id from the first sim data
        output_folder = os.path.join(self.output_path, exp_id)
        os.makedirs(output_folder, exist_ok=True)
        match_tuple = ("b", 2)
        b_result_list = []

        for sim, sim_data in all_data.items():
            # TODO: Add sim uid data
            if sim_data == match_tuple:
                b_result_list.append(sim_data)

        b_results_df = pd.DataFrame.from_records(b_result_list, columns=['key', 'value'])
        b_results_df.to_csv(os.path.join(output_folder, 'b_match.csv'), index_label='index')  # Write the matched sim results to a csv
