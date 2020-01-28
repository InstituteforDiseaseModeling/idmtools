# Example of a tags analyzer to get all the tags from your experiment simulations into one csv file

# First, import some necessary system and idmtools packages.
import os
import pandas as pd
from idmtools.entities import IAnalyzer


# Create a class for the analyzer
class TagsAnalyzer(IAnalyzer):
    # Arg option for analyzer init are uid, working_dir, parse (True to leverage the :class:`OutputParser`;
    # False to get the raw data in the :meth:`select_simulation_data`), and filenames
    # In this case, we want uid, working_dir, and parse=True
    def __init__(self, uid=None, working_dir=None, parse=True):
        super().__init__(uid, working_dir, parse)
        self.exp_id = None

    # Map is called to get for each simulation a data object (all the metadata of the simulations) and simulation object
    def map(self, data, simulation):
        df = pd.DataFrame(columns=simulation.tags.keys())  # Create a dataframe with the simulation tag keys
        df.loc[str(simulation.uid)] = list(simulation.tags.values())  # Get a list of the sim tag values
        df.index.name = 'SimId'  # Label the index keys you create with the names option
        return df

    # In reduce, we are printing the simulation and result data filtered in map
    def reduce(self, all_data):
        exp_id = str(next(iter(all_data.keys())).experiment.uid)  # Set the exp id from the first sim data
        results = pd.concat(list(all_data.values()), axis=0)  # Combine a list of all the sims tag values
        os.makedirs(exp_id, exist_ok=True)  # Make a directory labeled the exp id to write the tags to a csv
        results.to_csv(os.path.join(exp_id, 'tags.csv'))  # Write the sim tags to a csv
