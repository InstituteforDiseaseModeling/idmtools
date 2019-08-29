from idmtools.entities import IAnalyzer
from idmtools.managers import AnalyzeManager
from idmtools_platform_comps.COMPSPlatform import COMPSPlatform


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


p = COMPSPlatform()
am = AnalyzeManager(experiments=["185eb7fa-8f97-e911-a2bb-f0921c167866"],
                    analyzers=[ExampleAnalyzer(), ExampleAnalyzer2()],
                    platform=p)
am.analyze()
