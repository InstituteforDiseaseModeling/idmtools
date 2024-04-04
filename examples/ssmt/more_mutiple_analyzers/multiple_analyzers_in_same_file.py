import os
import sys
from typing import Dict, Any
from idmtools.analysis.platform_anaylsis import PlatformAnalysis
from idmtools.core.interfaces.iitem import IItem
from idmtools.core.platform_factory import Platform
from idmtools.entities import IAnalyzer


class ExampleAnalyzer(IAnalyzer):
    def __init__(self, filenames, uid=None, working_dir=None, parse=True):
        super().__init__(uid, working_dir, parse, filenames=filenames)

    def map(self, data, simulation):
        result = data[self.filenames[0]]
        return result

    # In reduce, we are printing the simulation and result data filtered in map
    def reduce(self, all_data):
        print("ExampleAnalyzer")
        for simulation, result in all_data.items():
            print(simulation)
            print(result)
            print("ExampleAnalyzer---")


class ExampleAnalyzer2(IAnalyzer):
    def __init__(self, filenames, uid=None, working_dir=None, parse=True):
        super().__init__(uid, working_dir, parse, filenames=filenames)

    def filter(self, simulation: IItem) -> bool:
        return int(simulation.tags.get("b")) > 1

    def map(self, data: Dict[str, Any], simulation: IItem):
        result = data[self.filenames[0]]
        return result

    def reduce(self, all_data: Dict[IItem, Any]):
        print("ExampleAnalyzer2")
        for simulation, result in all_data.items():
            print(simulation)
            print(result)
            print("ExampleAnalyzer2---")


if __name__ == "__main__":
    platform = Platform('CALCULON')
    analyzers = [ExampleAnalyzer, ExampleAnalyzer2]
    experiment_id = "31285dfc-4fe6-ee11-9f02-9440c9bee941"  # comps exp id
    analysis = PlatformAnalysis(platform, experiment_ids=[experiment_id], analyzers=analyzers, analyzers_args=[{'filenames': ['output/a.csv']}, {'filenames': ['config.json']}], analysis_name=os.path.split(sys.argv[0])[1])
    analysis.analyze(check_status=True)
    wi = analysis.get_work_item()
    print(wi)
