import json
import os
from typing import Dict, Any, Union
from idmtools.entities.ianalyzer import IAnalyzer as BaseAnalyzer

import matplotlib as mpl
from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools.entities.simulation import Simulation

mpl.use('Agg')


class PopulationAnalyzer(BaseAnalyzer):

    def __init__(self, title='idm'):
        super().__init__(filenames=["output\\InsetChart.json"])
        print(title)

    def initialize(self):
        """
        Initialize our Analyzer. At the moment, this just creates our output folder
        Returns:

        """
        if not os.path.exists(os.path.join(self.working_dir, "output")):
            os.mkdir(os.path.join(self.working_dir, "output"))

    def map(self, data: Dict[str, Any], item: Union[IWorkflowItem, Simulation]) -> Any:
        """
        Extracts the Statistical Population, Data channel from InsetChart.
        Called for Each WorkItem/Simulation.

        Args:
            data: Data mapping str to content of file
            item: Item to Extract Data from(Usually a Simulation)

        Returns:

        """
        return data[self.filenames[0]]["Channels"]["Statistical Population"]["Data"]

    def reduce(self, all_data: Dict[Union[IWorkflowItem, Simulation], Any]) -> Any:
        """

        Create the Final Population JSON and Plot
        Args:
            all_data: Populate data from all the Simulations

        Returns:
            None
        """
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
