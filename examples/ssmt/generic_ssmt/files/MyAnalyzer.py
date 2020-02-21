import json
import os
from typing import Any

from idmtools.core.interfaces.iitem import IItem

try:
    # use idmtools image
    from idmtools.entities.ianalyzer import IAnalyzer as BaseAnalyzer
except ImportError:
    # use dtk-tools image
    from simtools.Analysis.BaseAnalyzers.BaseAnalyzer import BaseAnalyzer

import matplotlib as mpl
mpl.use('Agg')


class PopulationAnalyzer(BaseAnalyzer):

    def __init__(self):
        super().__init__(filenames=["output\\InsetChart.json"])

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

    def initialize(self):
        if not os.path.exists(os.path.join(self.working_dir, "output")):
            os.mkdir(os.path.join(self.working_dir, "output"))

    # idmtools analyzer
    def map(self, data: Any, item: IItem) -> Any:
        return data[self.filenames[0]]["Channels"]["Statistical Population"]["Data"]

    def reduce(self, all_data: dict) -> Any:
        output_dir = os.path.join(self.working_dir, "output")
        with open(os.path.join(output_dir, "population.json"), "w") as fp:
            json.dump({str(s.uid): v for s, v in all_data.items()}, fp)
        import matplotlib.pyplot as plt
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for pop in list(all_data.values()):
            ax.plot(pop)
        ax.legend([str(s.uid) for s in all_data.keys()])
        fig.savefig(os.path.join(output_dir, "population.png"))
