from idmtools.entities import IAnalyzer
from idmtools.analysis.AnalyzeManager import AnalyzeManager
from idmtools.core.PlatformFactory import PlatformFactory


class ExampleAnalyzer(IAnalyzer):
    def __init__(self, uid=None, working_dir=None, parse=True):
        super().__init__(uid, working_dir, parse, filenames=["output.json"])

    def map(self, data, simulation):
        result = data["result"]
        return result

    def reduce(self, all_data):
        for simulation, result in all_data.items():
            print(simulation)
            print(result)
            print("---")


class ExampleAnalyzer2(IAnalyzer):
    def __init__(self, uid=None, working_dir=None, parse=True):
        super().__init__(uid, working_dir, parse, filenames=["config.json"])

    def filter(self, simulation: 'TSimulation') -> bool:
        return int(simulation.tags.get("a")) > 5

    def map(self, data, simulation):
        result = data["result"]
        return result

    def reduce(self, all_data):
        for simulation, result in all_data.items():
            print(simulation)
            print(result)
            print("---")


if __name__ == "__main__":

    platform = PlatformFactory.create(key='COMPS')

    analyzers = [ExampleAnalyzer(), ExampleAnalyzer2()]
    # analyzers = [ExampleAnalyzer2()]

    experiment_id = "91ec1e91-9fca-e911-a2bb-f0921c167866"  # "185eb7fa-8f97-e911-a2bb-f0921c167866"  # comps2 staging

    experiment = platform.get_item(id=experiment_id)

    manager = AnalyzeManager(configuration={}, platform=platform, items=experiment.children(), analyzers=analyzers)

    manager.analyze()
