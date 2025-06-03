# Example to demonstrate how to use analyzer's parse=False parameter to parse csv file as user defined
# In analyzer, default parse sets to True. So idmtools already parsed "data" filed in map() to dict{filename:dataframe}
# or dict{filename:dict of dataframe} for you. But if you want to parse file yourself, you can set Parse=False in
# __init__() function in your analyzer and in map function, you can read the file and parse it as needed.
# In this example, we parse a csv file in map() to include first row as content by reading csv file to dataframe.
import os
from io import BytesIO
from typing import Dict
import pandas as pd

from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities import IAnalyzer


class MyCSVAnalyzer(IAnalyzer):
    def __init__(self, filenames, parse=True, output_path="output"):
        super().__init__(parse=parse, filenames=filenames)
        self.output_path = output_path

    def initialize(self):
        self.output_path = os.path.join(self.working_dir, self.output_path)
        os.makedirs(self.output_path, exist_ok=True)

    def map(self, data, simulation) -> pd.DataFrame:
        # parse csv file ourself, 'data' contains a key as filename and value as csv byte string
        selected_df = pd.read_csv(BytesIO(data[self.filenames[0]]), skiprows=0, header=None)
        return selected_df

    def reduce(self, all_data: Dict):
        results = pd.concat(list(all_data.values()), axis=0,  # Combine a list of all the sims csv data column values
                            keys=[str(k.id) for k in all_data.keys()],  # Add sim id as index
                            names=['SimId'])  # as index name
        results.index = results.index.droplevel(1)  # Remove default index
        results = results.rename(columns={0: "Age", 1: "City"})  # add column titles

        # Make a directory labeled the exp id to write the csv results to
        first_sim = list(all_data.keys())[0]  # get first Simulation
        exp_id = str(first_sim.experiment.id)  # get experiment id from all_data
        output_folder = os.path.join(self.output_path, exp_id)
        os.makedirs(output_folder, exist_ok=True)
        results.to_csv(os.path.join(output_folder, self.__class__.__name__ + '.csv'))


if __name__ == '__main__':
    with Platform('CALCULON') as platform:

        # Arg option for analyzer init are uid, working_dir, data in the method map (aka select_simulation_data),
        # and filenames
        # In this case, we want to provide a filename to analyze
        filenames = ['output/b.csv']
        # Initialize the analyser class with the path of the output csv file
        analyzers = [MyCSVAnalyzer(filenames=filenames, parse=False)]

        # Set the experiment id you want to analyze
        experiment_id = '31285dfc-4fe6-ee11-9f02-9440c9bee941'  # comps exp id simple sim and csv example

        # Specify the id Type, in this case an Experiment on COMPS
        manager = AnalyzeManager(partial_analyze_ok=True, ids=[(experiment_id, ItemType.EXPERIMENT)],
                                 analyzers=analyzers)
        manager.analyze()