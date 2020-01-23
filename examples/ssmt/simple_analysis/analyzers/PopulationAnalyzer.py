import json
import os

try:
    # use idmtools image
    from idmtools.analysis.base_analyzer import BaseAnalyzer
except ImportError:
    # use dtk-tools image
    from simtools.Analysis.BaseAnalyzers.BaseAnalyzer import BaseAnalyzer

import matplotlib as mpl

mpl.use('Agg')


class PopulationAnalyzer(BaseAnalyzer):

    def __init__(self, title='idm'):
        super().__init__(filenames=["output\\InsetChart.json"])
        print(title)

    def initialize(self):
        if not os.path.exists(os.path.join(self.working_dir, "output")):
            os.mkdir(os.path.join(self.working_dir, "output"))

    def select_simulation_data(self, data, simulation):
        return data[self.filenames[0]]["Channels"]["Statistical Population"]["Data"]

    def finalize(self, all_data):
        # output directory to store json and image
        output_dir = os.path.join(self.working_dir, "output")

        with open(os.path.join(output_dir, "population.json"), "w") as fp:
            json.dump({s.id: v for s, v in all_data.items()}, fp)

        import matplotlib.pyplot as plt

        fig = plt.figure()
        ax = fig.add_subplot(111)

        for pop in list(all_data.values()):
            ax.plot(pop)
        ax.legend([s.id for s in all_data.keys()])
        fig.savefig(os.path.join(output_dir, "population.png"))
