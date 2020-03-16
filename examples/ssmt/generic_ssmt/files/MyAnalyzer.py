import json
import os
from typing import Any, Dict, Union
from idmtools.core.interfaces.iitem import IItem
from idmtools.entities.ianalyzer import IAnalyzer as BaseAnalyzer
import matplotlib as mpl
# Ensure Matplot lib is in console mode
from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools.entities.simulation import Simulation

mpl.use('Agg')


class PopulationAnalyzer(BaseAnalyzer):

    def __init__(self):
        super().__init__(filenames=["output\\InsetChart.json"])

    def initialize(self):
        """
        Perform our initialization. Here we ensure our output path exists
        Returns:

        """
        if not os.path.exists(os.path.join(self.working_dir, "output")):
            os.mkdir(os.path.join(self.working_dir, "output"))

    def map(self, data: Dict[str, Any], item: Union[IWorkflowItem, Simulation]) -> Any:
        """
        Executed for each Item(Simulation or WorkItem)

        Args:
            data: Mapping of Filenames to Binary data
            item: Workitem or Simulation

        Returns:

        """
        return data[self.filenames[0]]["Channels"]["Statistical Population"]["Data"]

    def reduce(self, all_data: Dict[Union[IWorkflowItem, Simulation], Any]) -> Any:
        """
        Called once we have gather all the data from our items

        Args:
            all_data: Dictionary mapping item to data

        Returns:

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
