import os
from logging import getLogger
from typing import Dict, Any, Union
from idmtools.entities.ianalyzer import IAnalyzer
from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools.entities.simulation import Simulation

logger = getLogger(__name__)


class DownloadAnalyzer(IAnalyzer):
    """
    A simple base class that will download the files specified in filenames without further treatment.

    Can be used by creating a child class:

    .. code-block:: python

        class InsetDownloader(DownloadAnalyzer):
            filenames = ['output/InsetChart.json']

    Or by directly calling it:

    .. code-block:: python

        analyzer = DownloadAnalyzer(filenames=['output/InsetChart.json'])


    Examples:
        .. literalinclude:: ../examples/analyzers/example_analysis_DownloadAnalyzer.py
    """

    def reduce(self, all_data: dict):
        pass

    def __init__(self, filenames=None, output_path="output", **kwargs):
        super().__init__(filenames=filenames, parse=False, **kwargs)
        self.output_path = output_path

    def initialize(self):
        self.output_path = os.path.join(self.working_dir, self.output_path)
        os.makedirs(self.output_path, exist_ok=True)

    def get_sim_folder(self, item):
        """
        Concatenate the specified top-level output folder with the simulation ID.

        Args:
            item: A simulation output parsing thread.

        Returns:
            The name of the folder to download this simulation's output to.
        """
        return os.path.join(self.output_path, str(item.uid))

    def map(self, data: Dict[str, Any], item: Union[IWorkflowItem, Simulation]):
        """
        Write the downloaded data to the path

        Args:
            data:
            item:

        Returns:

        """
        # Create a folder for the current simulation/item
        sim_folder = self.get_sim_folder(item)
        os.makedirs(sim_folder, exist_ok=True)

        # Create the requested files
        for filename in self.filenames:
            file_path = os.path.join(sim_folder, os.path.basename(filename))

            logger.debug(f'Writing to path: {file_path}')
            with open(file_path, 'wb') as outfile:
                outfile.write(data[filename])
