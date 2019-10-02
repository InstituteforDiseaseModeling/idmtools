from idmtools.analysis.AnalyzeManager import AnalyzeManager
from idmtools.core.PlatformFactory import PlatformFactory
from idmtools.entities import IAnalyzer


class ExampleAnalyzer(IAnalyzer):
    #TODO: Fix this example
    def __init__(self, uid=None, working_dir=None, parse=True):
        super().__init__(uid, working_dir, parse, filenames=["output/result.json"])

    def map(self, data, simulation):
        result = data[self.filenames[0]]
        return result

    def reduce(self, all_data):
        for simulation, result in all_data.items():
            print(simulation)
            print(result)
            print("ExampleAnalyzer---")


class ExampleAnalyzer2(IAnalyzer):
    def __init__(self, uid=None, working_dir=None, parse=True):
        super(ExampleAnalyzer2, self).__init__(uid, working_dir, parse, filenames=["config.json"])

    def filter(self, simulation: 'TSimulation') -> bool:
        return int(simulation.tags.get("b")) > 5

    def map(self, data, simulation):
        result = data[self.filenames[0]]
        return result

    def reduce(self, all_data):
        for simulation, result in all_data.items():
            print(simulation)
            print(result)
            print("ExampleAnalyzer2---")


if __name__ == "__main__":
    platform = PlatformFactory.create(key='COMPS')

    analyzers = [ExampleAnalyzer(), ExampleAnalyzer2()]

    experiment_id = "91ec1e91-9fca-e911-a2bb-f0921c167866"  ## comps2 staging

    manager = AnalyzeManager(configuration={}, platform=platform, ids=[experiment_id], analyzers=analyzers)
    manager.analyze()