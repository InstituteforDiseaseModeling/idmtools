import datetime
import os
import time
from typing import Any

from idmtools.entities.ianalyzer import IAnalyzer


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

    """

    def __init__(self, filenames=None, output_path=None, **kwargs):
        super(DownloadAnalyzer, self).__init__(**kwargs)

        self.output_path = output_path or "output"
        self.filenames = filenames or []
        self.start_time = None
        # We only want the raw files -> disable parsing
        self.parse = False

    def filter(self, item):
        return True  # download them all!

    def initialize(self):
        self.output_path = os.path.join(self.working_dir, self.output_path)
        os.makedirs(self.output_path, exist_ok=True)
        self.start_time = time.time()

    def get_sim_folder(self, item):
        """
        Concatenate the specified top-level output folder with the simulation ID.

        Args:
            item: A simulation output parsing thread.

        Returns:
            The name of the folder to download this simulation's output to.
        """
        return os.path.join(self.output_path, str(item.uid))

    def map(self, data, item):
        # Create a folder for the current simulation/item
        sim_folder = self.get_sim_folder(item)
        os.makedirs(sim_folder, exist_ok=True)

        ret = dict()
        # Create the requested files
        for filename in self.filenames:
            file_path = os.path.join(sim_folder, os.path.basename(filename))
            ret[filename] = file_path
            print('writing to path: %s' % file_path)
            with open(file_path, 'wb') as outfile:
                outfile.write(data[filename])
        return ret

    def reduce(self, all_data: dict) -> 'Any':
        finished = time.time()
        runtime = str(datetime.timedelta(seconds=(finished - self.start_time)))
        total_files = sum([len(x) for x in all_data.values()])
        print(f"Downloaded {total_files} in {runtime}")
