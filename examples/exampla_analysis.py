from idmtools.analysis import IAnalyzer
from idmtools.managers import AnalyzeManager


class ExampleAnalyzer(IAnalyzer):
    def __init__(self, uid=None, working_dir=None, parse=True):
        super().__init__(uid, working_dir, parse, filenames=["output.json"])

    def select_simulation_data(self, data, simulation):
        result = data["result"]
        return result

    def finalize(self, all_data):
        for simulation, result in all_data.items():
            print(simulation)
            print(result)
            print("---")


am = AnalyzeManager(experiments=["123"],
                    analyzers=[ExampleAnalyzer()])
am.analyze()
