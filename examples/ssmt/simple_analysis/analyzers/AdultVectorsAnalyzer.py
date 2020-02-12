import json
import os
from typing import Any, Dict
from uuid import UUID
from idmtools.core.interfaces.iitem import IItem
from idmtools.entities.simulation import Simulation

try:
    # use idmtools image
    from idmtools.entities.ianalyzer import BaseAnalyzer
except ImportError:
    # use dtk-tools image
    from simtools.Analysis.BaseAnalyzers.BaseAnalyzer import BaseAnalyzer

import matplotlib as mpl

mpl.use('Agg')


class AdultVectorsAnalyzer(BaseAnalyzer):

    def __init__(self, name='hi'):
        super().__init__(filenames=["output\\InsetChart.json"])
        print(name)

    def initialize(self):
        if not os.path.exists(os.path.join(self.working_dir, "output")):
            os.mkdir(os.path.join(self.working_dir, "output"))

    def select_simulation_data(self, data: Dict[str, Any], simulation: Simulation):
        return data[self.filenames[0]]["Channels"]["Adult Vectors"]["Data"]

    def finalize(self, all_data):
        # output directory to store json and image
        output_dir = os.path.join(self.working_dir, "output")
        with open(os.path.join(output_dir, "adult_vectors.json"), "w") as fp:
            json.dump({s.id: v for s, v in all_data.items()}, fp)

        import matplotlib.pyplot as plt

        fig = plt.figure()
        ax = fig.add_subplot(111)

        for pop in list(all_data.values()):
            ax.plot(pop)
        ax.legend([s.id for s in all_data.keys()])
        fig.savefig(os.path.join(output_dir, "adult_vectors.png"))

    def map(self, data: Any, item: IItem) -> Any:
        return None

    def reduce(self, all_data: Dict[UUID, Any]) -> Any:
        pass
