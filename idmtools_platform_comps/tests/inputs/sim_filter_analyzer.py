import os
import pandas as pd
import ast
from logging import getLogger
from idmtools.entities.ianalyzer import IAnalyzer

logger = getLogger(__name__)

# This tags analyzer is for test_sweep_* test cases with a, b, c tags and params


class SimFilterAnalyzer(IAnalyzer):

    def __init__(self, filenames=None, output_path="output", result_file_name="b_match.csv", **kwargs):
        super().__init__(filenames=filenames, parse=False, **kwargs)
        self.output_path = output_path
        self.result_file_name = result_file_name

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
        exp_id = str(first_sim.experiment.id)  # Set the exp id from the first sim data
        output_folder = os.path.join(self.output_path, exp_id)
        os.makedirs(output_folder, exist_ok=True)

        b_result_dict = {}

        for sim, sim_data in all_data.items():
            b_result_dict[sim.id] = sim_data

        df = pd.DataFrame.from_dict(b_result_dict,orient='index', columns=['tags', 'value'])
        df.to_csv(os.path.join(output_folder, self.result_file_name), index_label="sim_id")  # Write the matched sim results to a csv
