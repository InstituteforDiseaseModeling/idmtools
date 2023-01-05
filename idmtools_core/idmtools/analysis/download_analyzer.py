"""idmtools Download analyzer.

Download Analyzer.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
from logging import getLogger
from idmtools.entities.ianalyzer import IAnalyzer, ANALYSIS_REDUCE_DATA_TYPE, ANALYZABLE_ITEM, ANALYSIS_ITEM_MAP_DATA_TYPE

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
        .. literalinclude:: ../../examples/analyzers/example_analysis_DownloadAnalyzer.py
    """

    def reduce(self, all_data: ANALYSIS_REDUCE_DATA_TYPE):
        """
        Combine the :meth:`map` data for a set of items into an aggregate result. In this case, for downloading, we just ignore it because there is no reduction.

        Args:
            all_data: Dictionary in form item->map result where item is Simulations or WorkItems

        Returns:
            None
        """
        pass

    def __init__(self, filenames=None, output_path="output", **kwargs):
        """Constructor of the analyzer."""
        super().__init__(filenames=filenames, parse=False, **kwargs)
        self.output_path = output_path

    def initialize(self):
        """
        Initialize our sim. In this case, we create our output directory.

        Returns:
            None
        """
        self.output_path = os.path.join(self.working_dir, self.output_path)
        os.makedirs(self.output_path, exist_ok=True)

    def get_item_folder(self, item: ANALYZABLE_ITEM):
        """
        Concatenate the specified top-level output folder with the item ID.

        Args:
            item: A simulation output parsing thread.

        Returns:
            The name of the folder to download this simulation's output to.
        """
        return os.path.join(self.output_path, str(item.uid))

    def map(self, data: ANALYSIS_ITEM_MAP_DATA_TYPE, item: ANALYZABLE_ITEM):
        """
        Provide a map of filenames->data for each item. We then download each of these files to our output folder.

        Args:
            data: Map filenames->data
            item: Item we are mapping.

        Returns:
            None
        """
        # Create a folder for the current simulation/item
        sim_folder = self.get_item_folder(item)
        os.makedirs(sim_folder, exist_ok=True)

        # Create the requested files
        for filename in self.filenames:
            file_path = os.path.join(sim_folder, os.path.basename(filename))

            logger.debug(f'Writing to path: {file_path}')
            with open(file_path, 'wb') as outfile:
                outfile.write(data[filename])
