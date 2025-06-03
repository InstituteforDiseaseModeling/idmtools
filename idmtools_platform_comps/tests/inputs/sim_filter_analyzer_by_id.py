import os
import pandas as pd
from logging import getLogger
from idmtools.entities.ianalyzer import IAnalyzer

logger = getLogger(__name__)

# This tags analyzer is for test_sweep_* test cases with a, b, c tags and params


class SimFilterAnalyzerById(IAnalyzer):
    data_group_names = ['sim_id', 'key', 'value']

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
        return simulation.id != 'e6f2b1dc-7053-ea11-a2bf-f0921c167862'

    def map(self, data, simulation):
        df = pd.DataFrame(columns=simulation.tags.keys())  # Create a dataframe with the simulation tag keys
        df.loc[str(simulation.uid)] = list(simulation.tags.values())  # Get a list of the sim tag values
        df.index.name = 'SimId'  # Label the index keys you create with the names option
        return df

    def reduce(self, all_data):
        first_sim = list(all_data.keys())[0]  # get first Simulation
        exp_id = str(first_sim.experiment.id)  # Set the exp id from the first sim data
        output_folder = os.path.join(self.output_path, exp_id)
        os.makedirs(output_folder, exist_ok=True)
        results = pd.concat(list(all_data.values()), axis=0, sort=False)  # Combine a list of all the sims tag values
        results.to_csv(os.path.join(output_folder, 'result.csv'))  # Write the sim tags to a csv
