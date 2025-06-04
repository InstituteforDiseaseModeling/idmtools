"""idmtools CSVAnalyzer.

Example of a csv analyzer to concatenate csv results into one csv from your experiment's simulations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
from typing import Dict
import pandas as pd
from idmtools.entities import IAnalyzer
from idmtools.entities.ianalyzer import ANALYSIS_ITEM_MAP_DATA_TYPE, ANALYZABLE_ITEM


class CSVAnalyzer(IAnalyzer):
    """
    Provides an analyzer for CSV output.

    Examples:
        .. _simple-csv-example:

        Simple Example
          This example covers the basic usage of the CSVAnalyzer

          .. literalinclude:: ../../examples/analyzers/example_analysis_CSVAnalyzer.py

        .. _multiple-csvs:

        Multiple CSVs
            This example covers analyzing multiple CSVs

            .. literalinclude:: ../../examples/analyzers/example_analysis_MultiCSVAnalyzer.py
    """
    # Arg option for analyzer init are uid, working_dir, parse (True to leverage the :class:`OutputParser`;
    # False to get the raw data in the :meth:`select_simulation_data`), and filenames
    # In this case, we want parse=True, and the filename(s) to analyze
    def __init__(self, filenames, output_path="output_csv"):
        """
        Initialize our analyzer.

        Args:
            filenames: Filenames we want to pull
            output_path: Output path to write the csv
        """
        super().__init__(parse=True, filenames=filenames)
        # Raise exception early if files are not csv files
        if not all(['csv' in os.path.splitext(f)[1].lower() for f in self.filenames]):
            raise Exception('Please ensure all filenames provided to CSVAnalyzer have a csv extension.')

        self.output_path = output_path

    def initialize(self):
        """
        Initialize on run. Create an output directory.

        Returns:
            None
        """
        self.output_path = os.path.join(self.working_dir, self.output_path)

        # Create the output path
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    # Map is called to get for each simulation a data object (all the metadata of the simulations) and simulation object
    def map(self, data: ANALYSIS_ITEM_MAP_DATA_TYPE, simulation: ANALYZABLE_ITEM) -> pd.DataFrame:
        """
        Map each simulation/workitem data here.

        The data is a mapping of files -> content(in this case, dataframes since it is csvs parsed).

        Args:
            data: Data mapping of files -> content
            simulation: Simulation/Workitem we are mapping

        Returns:
            Items joined together into a dataframe.
        """
        # If there are 1 to many csv files, concatenate csv data columns into one dataframe
        concatenated_df = pd.concat(list(data.values()), axis=0, ignore_index=True, sort=True)
        return concatenated_df

    # In reduce, we are printing the simulation and result data filtered in map
    def reduce(self, all_data: Dict[ANALYZABLE_ITEM, pd.DataFrame]):
        """
        Reduce(combine) all the data from our mapping.

        Args:
            all_data: Mapping of our data in form Item(Simulation/Workitem) -> Mapped dataframe

        Returns:
            None
        """
        results = pd.concat(list(all_data.values()), axis=0,  # Combine a list of all the sims csv data column values
                            keys=[str(k.uid) for k in all_data.keys()],  # Add a hierarchical index with the keys option
                            names=['SimId'])  # Label the index keys you create with the names option
        results.index = results.index.droplevel(1)  # Remove default index

        # Make a directory labeled the exp id to write the csv results to
        first_sim = list(all_data.keys())[0]  # get first Simulation
        exp_id = first_sim.experiment.id  # Set the exp id from the first sim data
        output_folder = os.path.join(self.output_path, exp_id)
        os.makedirs(output_folder, exist_ok=True)
        results.to_csv(os.path.join(output_folder, self.__class__.__name__ + '.csv'))
