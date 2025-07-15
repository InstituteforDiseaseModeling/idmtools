import json
import os
from typing import Any, Dict, Union
from idmtools.entities.ianalyzer import IAnalyzer as BaseAnalyzer
import matplotlib as mpl
from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools.entities.simulation import Simulation

mpl.use('Agg')


class ExampleAnalyzer(BaseAnalyzer):

    def __init__(self, name='hi'):
        super().__init__(filenames=["stdout.txt"])
        print(name)

    def initialize(self):
        """
        Perform the Initialization of Analyzer
        Here we ensure our output directory exists
        Returns:

        """
        if not os.path.exists(os.path.join(self.working_dir, "output")):
            os.mkdir(os.path.join(self.working_dir, "output"))

    def map(self, data: Dict[str, Any], item: Union[IWorkflowItem, Simulation]) -> Any:
        """
        Select the Adult Vectors channel for the InsertChart

        Args:
            data: A dictionary that contains a mapping of filename to data
            item: Item can be a Simulation or WorkItem

        Returns:

        """
        return data[self.filenames[0]]

    def reduce(self, all_data: Dict[Union[IWorkflowItem, Simulation], Any]) -> Any:
        """
        Creates the final adult_vectors.json and Plot

        Args:
            all_data: Dictionary mapping our Items to the mapped data

        Returns:

        """
        output_dir = os.path.join(self.working_dir, "output")
        with open(os.path.join(output_dir, "std.txt"), "w") as fp:
            json.dump({str(s.uid): v for s, v in all_data.items()}, fp)

