from idmtools.analysis.AnalyzeManager import AnalyzeManager
from idmtools.core.platform_factory import Platform
from idmtools.entities import IAnalyzer


class ExampleAnalyzer(IAnalyzer):
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
        super().__init__(uid, working_dir, parse, filenames=["config.json"])

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
    platform = Platform('COMPS')

    analyzers = [ExampleAnalyzer(), ExampleAnalyzer2()]

    experiment_id = "11052582-83da-e911-a2be-f0921c167861" # comps2 staging

    manager = AnalyzeManager(platform=platform, ids=[experiment_id], analyzers=analyzers)
    manager.analyze()
