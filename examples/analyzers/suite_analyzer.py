# Example of multiple Analyzers for EMOD Experiments
# In this example, we will demonstrate analyzers that analyze different simulation output file types
# The 2nd example demonstrates how to use filter in an analyzer

# First, import some necessary system and idmtools packages.
from typing import Dict, Any
from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.core import ItemType
from idmtools.core.interfaces.iitem import IItem
from idmtools.core.platform_factory import Platform
from idmtools.entities import IAnalyzer


# Create a class for your analyzer
class ExampleAnalyzer(IAnalyzer):
    # Arg option for analyzer init are uid, working_dir, parse (True to leverage the :class:`OutputParser`;
    # False to get the raw data in the :meth:`select_simulation_data`), and filenames
    # In this case, we want to provide a uid, working_dir, parse=True, and filename to analyze
    def __init__(self, uid=None, working_dir=None, parse=True):
        super().__init__(uid, working_dir, parse, filenames=["output/result.json"])

    # Map is called to get for each simulation a data object (all the metadata of the simulations) and simulation object
    def map(self, data, simulation):
        result = data[self.filenames[0]]
        return result

    # In reduce, we are printing the simulation and result data filtered in map
    def reduce(self, all_data):
        for simulation, result in all_data.items():
            print(simulation)
            print(result)
            print("ExampleAnalyzer---")


# Create a class for another analyzer demonstrating an example of filtering simulations
class ExampleAnalyzer2(IAnalyzer):
    # Arg option for analyzer init are uid, working_dir, parse (True to leverage the :class:`OutputParser`;
    # False to get the raw data in the :meth:`select_simulation_data`), and filenames
    # In this case, we want to provide a uid, working_dir, parse=True, and filename to analyze
    def __init__(self, uid=None, working_dir=None, parse=True):
        super().__init__(uid, working_dir, parse, filenames=["config.json"])

    # Filter for simulations with a particular tag value greater than a value
    def filter(self, simulation: IItem) -> bool:
        return int(simulation.tags.get("Run_Number")) > 5

    # Map is called to get for each simulation a data object (all the metadata of the simulations) and simulation object
    def map(self, data: Dict[str, Any], simulation: IItem):
        result = data[self.filenames[0]]
        return result

    # In reduce, we are printing the simulation and result data filtered in map
    def reduce(self, all_data: Dict[IItem, Any]):
        for simulation, result in all_data.items():
            print(simulation)
            print(result)
            print("ExampleAnalyzer2---")


class ExampleAnalyzer3(IAnalyzer):
    def __init__(self, uid=None, working_dir=None, parse=True, filenames=None):
        super().__init__(uid, working_dir, parse, filenames=filenames)

    def map(self, data, simulation):
        result = data[self.filenames[0]]
        return result

    def reduce(self, all_data):
        for simulation, result in all_data.items():
            print(simulation)
            print(result)
            print("ExampleAnalyzer---")


if __name__ == "__main__":
    # Set the platform where you want to run your analysis
    with Platform('CALCULON') as platform:

        # Initialize the analyser class with the name of file to save to and start the analysis
        analyzers = [ExampleAnalyzer2()]

        # Set the experiment and simulation ids you want to analyze
        suite_tuple = ('2a23f67b-7836-f011-aa20-b88303911bc1', ItemType.SUITE)
        experiment_tuple = ('2b23f67b-7836-f011-aa20-b88303911bc1', ItemType.EXPERIMENT)  # comps exp id
        simulation_tuple = ("75783286-7836-f011-aa20-b88303911bc1", ItemType.SIMULATION)  # comps sim id

        # case #0: normal case with experiment id list. --OK
        manager = AnalyzeManager(ids=[suite_tuple], analyzers=analyzers, max_workers=1)
        manager.analyze()
