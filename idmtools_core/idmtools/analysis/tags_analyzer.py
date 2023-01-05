"""
Example of a tags analyzer to get all the tags from your experiment simulations into one csv file.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
# First, import some necessary system and idmtools packages.
import os
from typing import Dict, Any

import pandas as pd
from idmtools.entities import IAnalyzer

# Create a class for the analyzer
from idmtools.entities.ianalyzer import ANALYZABLE_ITEM


class TagsAnalyzer(IAnalyzer):
    """
    Provides an analyzer for CSV output.

    Examples:
        .. literalinclude:: ../../examples/analyzers/example_analysis_TagsAnalyzer.py
    """

    # Arg option for analyzer init are uid, working_dir, parse (True to leverage the :class:`OutputParser`;
    # False to get the raw data in the :meth:`select_simulation_data`), and filenames
    # In this case, we want uid, working_dir, and parse=True
    def __init__(self, uid=None, working_dir=None, parse=True, output_path="output_tag"):
        """
        Initialize our Tags Analyzer.

        Args:
            uid:
            working_dir:
            parse:
            output_path:

        See Also:
            :class:`~idmtools.entities.ianalyzer.IAnalyzer`.
        """
        super().__init__(uid, working_dir, parse)
        self.exp_id = None
        self.output_path = output_path

    def initialize(self):
        """
        Initialize the item before mapping data. Here we create a directory for the output.

        Returns:
            None
        """
        self.output_path = os.path.join(self.working_dir, self.output_path)

        # Create the output path
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    # Map is called to get for each simulation a data object (all the metadata of the simulations) and simulation object
    def map(self, data: Dict[str, Any], simulation: ANALYZABLE_ITEM):
        """
        Map our data for our Workitems/Simulations. In this case, we just extract the tags and build a dataframe from those.

        Args:
            data: List of files. This should be empty for us.
            simulation: Item to extract

        Returns:
            Data frame with the tags built.
        """
        df = pd.DataFrame(columns=list(simulation.tags.keys()))  # Create a dataframe with the simulation tag keys
        df.loc[str(simulation.uid)] = list(simulation.tags.values())  # Get a list of the sim tag values
        df.index.name = 'SimId'  # Label the index keys you create with the names option
        return df

    # In reduce, we are printing the simulation and result data filtered in map
    def reduce(self, all_data: Dict[ANALYZABLE_ITEM, pd.DataFrame]):
        """
        Reduce the dictionary of items->Tags dataframe to a single dataframe and write to a csv file.

        Args:
            all_data: Map of Item->Tags dataframe

        Returns:
            None
        """
        results = pd.concat(list(all_data.values()), axis=0)  # Combine a list of all the sims tag values

        # Make a directory labeled the exp id to write the csv results to
        first_sim = list(all_data.keys())[0]  # get first Simulation
        exp_id = first_sim.experiment.id  # Set the exp id from the first sim data
        output_folder = os.path.join(self.output_path, exp_id)
        os.makedirs(output_folder, exist_ok=True)
        results.to_csv(os.path.join(output_folder, self.__class__.__name__ + '.csv'))
