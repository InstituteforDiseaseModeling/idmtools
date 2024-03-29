import os
import pandas as pd
from typing import Any

from idmtools.core.interfaces.iitem import IItem

from idmtools.entities.ianalyzer import IAnalyzer as BaseAnalyzer
import matplotlib as mpl
mpl.use('Agg')


# Create a class for the analyzer
class CSVAnalyzer(BaseAnalyzer):
    # Arg option for analyzer init are uid, working_dir, parse (True to leverage the :class:`OutputParser`;
    # False to get the raw data in the :meth:`select_simulation_data`), and filenames
    # In this case, we want parse=True, and the filename(s) to analyze
    def __init__(self, filenames, parse=True):
        super().__init__(filenames=filenames, parse=parse)
        # # Raise exception early if files are not csv files
        if not all(['csv' in os.path.splitext(f)[1].lower() for f in self.filenames]):
            raise Exception('Please ensure all filenames provided to CSVAnalyzer have a csv extension.')

    def initialize(self):
        if not os.path.exists(os.path.join(self.working_dir, "output")):
            os.mkdir(os.path.join(self.working_dir, "output"))

    # Map is called to get for each simulation a data object (all the metadata of the simulations) and simulation object
    def map(self, data: Any, item: IItem) -> Any:
        # If there are 1 to many csv files, concatenate csv data columns into one dataframe
        concatenated_df = pd.concat(list(data.values()), axis=0, ignore_index=True, sort=True)
        return concatenated_df

    # In reduce, we are printing the simulation and result data filtered in map
    def reduce(self, all_data: dict) -> Any:
        output_folder = os.path.join(self.working_dir, "output")
        results = pd.concat(list(all_data.values()), axis=0,  # Combine a list of all the sims csv data column values
                            keys=[str(k.uid) for k in all_data.keys()],  # Add a hierarchical index with the keys option
                            names=['SimId'])  # Label the index keys you create with the names option
        results.index = results.index.droplevel(1)  # Remove default index

        # NOTE: If running twice with different filename, the output files will collide
        results.to_csv(os.path.join(output_folder, 'aggregated_c.csv'))
