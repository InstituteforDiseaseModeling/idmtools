import os

from idmtools.analysis.AnalyzeManager import AnalyzeManager
from idmtools.core.platform_factory import Platform
from idmtools.entities import IAnalyzer


class PopulationAnalyzer(IAnalyzer):
    def __init__(self, filenames=None):
        super().__init__()
        self.filenames = filenames or []

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

    platform = Platform('COMPS2')

    exp_id = '65a93d51-04db-e911-a2be-f0921c167861' # comps2 exp_id

    filenames = ['output/InsetChart.json']
    analyzers = [PopulationAnalyzer(filenames=filenames)]

    manager = AnalyzeManager( platform=platform, ids=[exp_id], analyzers=analyzers)
    manager.analyze()
