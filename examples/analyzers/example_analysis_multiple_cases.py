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
    platform = Platform('COMPS')

    analyzers = [ExampleAnalyzer(), ExampleAnalyzer2()]

    experiment_id = "11052582-83da-e911-a2be-f0921c167861"  ## comps2 staging
    experiment = platform.get_item(id=experiment_id)

    # case #0: normal case with experiment id list. --OK
    manager = AnalyzeManager(platform=platform, ids=[experiment_id], analyzers=analyzers)
    manager.analyze()

    # case #1: test add_analyzer() --OK
    manager1 = AnalyzeManager(platform=platform, ids=[experiment_id])
    manager1.add_analyzer(ExampleAnalyzer())
    manager1.add_analyzer(ExampleAnalyzer2())
    manager1.analyze()

    # case #2: test add_item(experiment) --failed at  manager.add_item(experiment)
    manager2 = AnalyzeManager(platform=platform, analyzers=analyzers)
    manager2.add_item(experiment)
    manager2.analyze()

    # case #3: test add_item(simulation) --failed at platform.get_item
    simulation_id = "a042c9a2-60d6-e911-a2bb-f0921c167866"  ## comps2 staging sim id
    simulation = platform.get_item(id=simulation_id)
    manager3 = AnalyzeManager(platform=platform, analyzers=analyzers)
    manager3.add_item(simulation)
    manager3.analyze()

    # case #4: old experiment_id
    filenames = ['output/InsetChart.json']
    analyzer3 = [ExampleAnalyzer3(filenames=filenames)]
    manager4 = AnalyzeManager(platform=platform, ids=["f36ffd16-19da-e911-a2be-f0921c167861"],
                              analyzers=analyzer3)
    manager4.analyze()

    #case #5: analyzer with simulation
    manager5 = AnalyzeManager(platform=platform, ids=['a042c9a2-60d6-e911-a2bb-f0921c167866'], analyzers=analyzers)
    manager5.analyze()
