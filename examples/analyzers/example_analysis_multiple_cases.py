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
        return int(simulation.tags.get("b")) > 5

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
        analyzers = [ExampleAnalyzer(), ExampleAnalyzer2()]

        # Set the experiment and simulation ids you want to analyze
        experiment_tuple = ('40c1b14d-0a04-eb11-a2c7-c4346bcb1553', ItemType.EXPERIMENT)  # comps exp id
        simulation_tuple = ("45c1b14d-0a04-eb11-a2c7-c4346bcb1553", ItemType.SIMULATION)  # comps sim id

        # case #0: normal case with experiment id list. --OK
        manager = AnalyzeManager(ids=[experiment_tuple], analyzers=analyzers)
        manager.analyze()

        # case #1: test add_analyzer() --OK
        manager1 = AnalyzeManager(ids=[experiment_tuple])
        manager1.add_analyzer(ExampleAnalyzer())
        manager1.add_analyzer(ExampleAnalyzer2())
        manager1.analyze()

        # case #2: test add_item(experiment) --failed at  manager.add_item(experiment)
        manager2 = AnalyzeManager(analyzers=analyzers)
        experiment = platform.get_item(item_id=experiment_tuple[0], item_type=ItemType.EXPERIMENT)
        manager2.add_item(experiment)
        manager2.analyze()

        # case #3: test add_item(simulation) --failed at platform.get_item
        simulation = platform.get_item(item_id=simulation_tuple[0], item_type=ItemType.SIMULATION)
        manager3 = AnalyzeManager(analyzers=analyzers, partial_analyze_ok=True)
        manager3.add_item(simulation)
        manager3.analyze()

        # case #4: old experiment_id
        filenames = ['output/result.json']
        analyzer3 = [ExampleAnalyzer3(filenames=filenames)]
        manager4 = AnalyzeManager(ids=[experiment_tuple],
                                  analyzers=analyzer3)
        manager4.analyze()

        #case #5: analyzer with simulation
        manager5 = AnalyzeManager(ids=[simulation_tuple], analyzers=analyzers)
        manager5.analyze()

        #case #6: analyzer with exclude id
        analyzers = [ExampleAnalyzer()]
        exclude_ids = ["43c1b14d-0a04-eb11-a2c7-c4346bcb1553", "42c1b14d-0a04-eb11-a2c7-c4346bcb1553"]  #comps sim ids
        manager6 = AnalyzeManager(ids=[experiment_tuple], analyzers=analyzers, exclude_ids=exclude_ids)
        manager6.analyze()

