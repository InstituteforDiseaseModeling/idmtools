# Example of a tags analyzer to get all the tags from your experiment simulations into one csv file

# First, import some necessary system and idmtools packages.
import os
import pandas as pd
from idmtools.entities import IAnalyzer


# Create a class for the analyzer
class TagsAnalyzer(IAnalyzer):
    """
    Provides an analyzer for CSV output

    Examples:
        .. literalinclude:: ../examples/analyzers/example_analysis_TagsAnalyzer.py
    """

    # Arg option for analyzer init are uid, working_dir, parse (True to leverage the :class:`OutputParser`;
    # False to get the raw data in the :meth:`select_simulation_data`), and filenames
    # In this case, we want uid, working_dir, and parse=True
    def __init__(self, uid=None, working_dir=None, parse=True):
        super().__init__(uid, working_dir, parse)
        self.exp_id = None

    def initialize(self):
        if not os.path.exists(os.path.join(self.working_dir, "output_tag")):
            os.mkdir(os.path.join(self.working_dir, "output_tag"))

    # Map is called to get for each simulation a data object (all the metadata of the simulations) and simulation object
    def map(self, data, simulation):
        df = pd.DataFrame(columns=simulation.tags.keys())  # Create a dataframe with the simulation tag keys
        df.loc[str(simulation.uid)] = list(simulation.tags.values())  # Get a list of the sim tag values
        df.index.name = 'SimId'  # Label the index keys you create with the names option
        return df

    # In reduce, we are printing the simulation and result data filtered in map
    def reduce(self, all_data):
        results = pd.concat(list(all_data.values()), axis=0)  # Combine a list of all the sims tag values
        results.to_csv(os.path.join("output_tag", 'tags.csv'))  # Write the sim tags to a csv
