# Example of a csv analyzer to concatenate csv results into one csv from your experiment simulations

# First, import some necessary system and idmtools packages.
import os
import pandas as pd
from idmtools.entities import IAnalyzer


# Create a class for the analyzer
class CSVAnalyzer(IAnalyzer):
    """
    Provides an analyzer for CSV output

    Examples:

        .. _simple-csv-example:

        Simple Example
          This example covers the basic usage of the CSVAnalyzer

          .. literalinclude:: ../examples/analyzers/example_analysis_CSVAnalyzer.py

        .. _multiple-csvs:

        Multiple CSVs
            This example covers analyzing multiple CSVs

            .. literalinclude:: ../examples/analyzers/example_analysis_MultiCSVAnalyzer.py
    """

    # Arg option for analyzer init are uid, working_dir, parse (True to leverage the :class:`OutputParser`;
    # False to get the raw data in the :meth:`select_simulation_data`), and filenames
    # In this case, we want parse=True, and the filename(s) to analyze
    def __init__(self, filenames, parse=True, output_path=None):
        super().__init__(parse=parse, filenames=filenames)
        # Raise exception early if files are not csv files
        if not all(['csv' in os.path.splitext(f)[1].lower() for f in self.filenames]):
            raise Exception('Please ensure all filenames provided to CSVAnalyzer have a csv extension.')

        self.output_path = output_path or "output_csv"

    def initialize(self):
        self.output_path = os.path.join(self.working_dir, self.output_path)

        # Create the output path
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    # Map is called to get for each simulation a data object (all the metadata of the simulations) and simulation object
    def map(self, data, simulation):
        # If there are 1 to many csv files, concatenate csv data columns into one dataframe
        concatenated_df = pd.concat(list(data.values()), axis=0, ignore_index=True, sort=True)
        return concatenated_df

    # In reduce, we are printing the simulation and result data filtered in map
    def reduce(self, all_data):

        results = pd.concat(list(all_data.values()), axis=0,  # Combine a list of all the sims csv data column values
                            keys=[str(k.uid) for k in all_data.keys()],  # Add a hierarchical index with the keys option
                            names=['SimId'])  # Label the index keys you create with the names option
        results.index = results.index.droplevel(1)  # Remove default index

        # Make a directory labeled the exp id to write the csv results to
        first_sim = next(iter(all_data.keys()))  # Iterate over the dataframe keys
        exp_id = first_sim.experiment.id  # Set the exp id from the first sim data
        output_folder = os.path.join(self.output_path, exp_id)
        os.makedirs(output_folder, exist_ok=True)
        results.to_csv(os.path.join(output_folder, self.__class__.__name__ + '.csv'))
