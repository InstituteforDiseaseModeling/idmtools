import json
import os

try:
    # use idmtools image
    from idmtools.entities.ianalyzer import IAnalyzer as BaseAnalyzer
except ImportError:
    # use dtk-tools image
    from simtools.Analysis.BaseAnalyzers.BaseAnalyzer import BaseAnalyzer

import matplotlib as mpl

mpl.use('Agg')


class PopulationAnalyzer(BaseAnalyzer):

    def __init__(self,  working_dir="."):
        super().__init__(filenames=["output\\InsetChart.json"], working_dir=working_dir)
        self.dir_name = "output"

    def map(self, data, simulation):
        return data[self.filenames[0]]["Channels"]["Statistical Population"]["Data"]

    def reduce(self, all_data):
        output_path = os.path.join(self.working_dir, self.dir_name)
        if not os.path.exists(output_path):
            os.mkdir(output_path)

        with open(os.path.join(output_path, "results.json"), "w") as fp:
            json.dump({s.id: v for s, v in all_data.items()}, fp)

        import matplotlib.pyplot as plt

        fig = plt.figure()
        ax = fig.add_subplot(111)

        for pop in list(all_data.values()):
            ax.plot(pop)
        ax.legend([s.id for s in all_data.keys()])
        fig.savefig(os.path.join(output_path, "figure.png"))
