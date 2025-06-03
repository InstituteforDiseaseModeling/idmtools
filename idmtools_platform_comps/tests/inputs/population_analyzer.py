import json
import os
from typing import Any

from idmtools.core.interfaces.iitem import IItem
from idmtools.entities.ianalyzer import IAnalyzer as BaseAnalyzer
import matplotlib as mpl

mpl.use('Agg')


class PopulationAnalyzer(BaseAnalyzer):

    def __init__(self, working_dir=".", name='idm', output_path="output"):
        super().__init__(filenames=["output\\InsetChart.json"], working_dir=working_dir)
        print(name)
        self.output_path = output_path

    def initialize(self):
        self.output_path = os.path.join(self.working_dir, self.output_path)

        # Create the output path
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    # idmtools analyzer
    def map(self, data: Any, item: IItem) -> Any:
        return data[self.filenames[0]]["Channels"]["Statistical Population"]["Data"]

    def reduce(self, all_data: dict) -> Any:
        first_sim = list(all_data.keys())[0]  # get first Simulation
        exp_id = str(first_sim.experiment.id)  # Set the exp id from the first sim data
        output_folder = os.path.join(self.output_path, exp_id)
        os.makedirs(output_folder, exist_ok=True)

        with open(os.path.join(output_folder, "population.json"), "w") as fp:
            json.dump({str(s.uid): v for s, v in all_data.items()}, fp)

        import matplotlib.pyplot as plt

        fig = plt.figure()
        ax = fig.add_subplot(111)

        for pop in list(all_data.values()):
            ax.plot(pop)
        ax.legend([str(s.uid) for s in all_data.keys()])
        fig.savefig(os.path.join(output_folder, "population.png"))

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
