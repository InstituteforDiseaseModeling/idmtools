import os

from idmtools.analysis.AnalyzeManager import AnalyzeManager
from idmtools.entities import IAnalyzer
from idmtools.core.PlatformFactory import PlatformFactory


class PopulationAnalyzer(IAnalyzer):
    def __init__(self):
        filenames = ['output/InsetChart.json']
        super().__init__(filenames=filenames)

    def map(self, data, simulation):
        # Apply is called for every simulations included into the experiment
        # We are simply storing the population data in the pop_data dictionary
        return data[self.filenames[0]]["Channels"]["Statistical Population"]["Data"]

    def reduce(self, all_data):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig = plt.figure()
        for pop in list(all_data.values()):
            plt.plot(pop)
        plt.legend([s.id for s in all_data.keys()])
        plt.savefig(os.path.join(os.getcwd(), 'Population.png'))
        plt.close(fig)


if __name__ == "__main__":

    platform = PlatformFactory.create(key='COMPS')

    exp_id = '31d83b39-85b4-e911-a2bb-f0921c167866' #'86099829-6ecb-e911-a2bb-f0921c167866'

    analyzers = [PopulationAnalyzer()]

    experiment = platform.get_item(id=exp_id)

    manager = AnalyzeManager(configuration={}, platform=platform, items=experiment.children(), analyzers=analyzers)
    manager.analyze()
