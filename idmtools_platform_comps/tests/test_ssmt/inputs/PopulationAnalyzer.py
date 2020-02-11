import json
import os
import pandas as pd

# uncomment following lines with idmtools image of ssmt
# from idmtools.analysis.analyze_manager import AnalyzeManager
# from idmtools.core import ItemType
# from idmtools.core.platform_factory import Platform

try:
    # use idmtools image
    from idmtools.entities.ianalyzer import IAnalyzer as BaseAnalyzer
except ImportError:
    # use dtk-tools image
    from simtools.Analysis.BaseAnalyzers.BaseAnalyzer import BaseAnalyzer

import matplotlib as mpl

mpl.use('Agg')


class PopulationAnalyzer(BaseAnalyzer):

    def __init__(self, working_dir=".", name='idm'):
        super().__init__(filenames=["output\\InsetChart.json"], working_dir=working_dir)
        print(name)

    def initialize(self):
        if not os.path.exists(os.path.join(self.working_dir, "output")):
            os.mkdir(os.path.join(self.working_dir, "output"))

    # idmtools analyzer
    def map(self, data, simulation):
        return data[self.filenames[0]]["Channels"]["Statistical Population"]["Data"]

    def reduce(self, all_data):
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

    # dtk-tools analyzer
    def select_simulation_data(self, data, simulation):
        return data[self.filenames[0]]["Channels"]["Statistical Population"]["Data"]

    def finalize(self, all_data):
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

# uncomment following lines with idmtools analyzer
# if __name__ == "__main__":
#     platform = Platform('COMPS2')
#
#     filenames = ['output/InsetChart.json']
#     analyzers = [PopulationAnalyzer(working_dir=".")]
#
#     exp_id = '8bb8ae8f-793c-ea11-a2be-f0921c167861'  # comps2 exp_id
#     manager = AnalyzeManager(platform=platform, ids=[(exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
#     manager.analyze()
