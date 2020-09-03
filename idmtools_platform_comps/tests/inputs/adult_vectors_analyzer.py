import json
import os
from typing import Any

from idmtools.core.interfaces.iitem import IItem

from idmtools.entities.ianalyzer import IAnalyzer as BaseAnalyzer
import matplotlib as mpl

mpl.use('Agg')


class AdultVectorsAnalyzer(BaseAnalyzer):

    def __init__(self, name='hi', output_path="output"):
        super().__init__(filenames=["output\\InsetChart.json"])
        print(name)
        self.output_path = output_path

    def initialize(self):
        self.output_path = os.path.join(self.working_dir, self.output_path)

        # Create the output path
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    def map(self, data: Any, item: IItem) -> Any:
        return data[self.filenames[0]]["Channels"]["Adult Vectors"]["Data"]

    def reduce(self, all_data: dict) -> Any:
        first_sim = list(all_data.keys())[0]  # get first Simulation
        exp_id = first_sim.experiment.id  # Set the exp id from the first sim data
        output_folder = os.path.join(self.output_path, exp_id)
        os.makedirs(output_folder, exist_ok=True)
        with open(os.path.join(output_folder, "adult_vectors.json"), "w") as fp:
            json.dump({str(s.uid): v for s, v in all_data.items()}, fp)

        import matplotlib.pyplot as plt

        fig = plt.figure()
        ax = fig.add_subplot(111)

        for pop in list(all_data.values()):
            ax.plot(pop)
        ax.legend([str(s.uid) for s in all_data.keys()])
        fig.savefig(os.path.join(output_folder, "adult_vectors.png"))
