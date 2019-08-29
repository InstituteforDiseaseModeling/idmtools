import os

from idmtools.entities.IAnalyzer import IAnalyzer


class DownloadAnalyzer(IAnalyzer):
    """
    Download Analyzer
    A simple base class that will download the files specified in filenames without further treatment.

    Can be used by creating a child class:

    .. code-block:: python

        class InsetDownloader(DownloadAnalyzer):
            filenames = ['output/InsetChart.json']

    Or by directly calling it:

    .. code-block:: python

        analyzer = DownloadAnalyzer(filenames=['output/InsetChart.json'])

    """
    def __init__(self, filenames=None, output_path='output'):
        super().__init__()
        self.output_path = output_path
        self.filenames = filenames or []

        # We only want the raw files -> disable parsing
        self.parse = False

    def filter(self, item):
        return True  # download them all!

    def initialize(self):
        self.output_path = os.path.join(self.working_dir, self.output_path)
        os.makedirs(self.output_path, exist_ok=True)

    def get_sim_folder(self, item):
        """
        Concatenate the specified top-level output folder with the simulation ID
        :param parser: A simulation output parsing thread
        :return: The name of the folder to download this simulation's output to
        """
        return os.path.join(self.output_path, str(item.uid))

    def map(self, data, item):
        # Create a folder for the current simulation/item
        sim_folder = self.get_sim_folder(item)
        os.makedirs(sim_folder, exist_ok=True)

        # Create the requested files
        for filename in self.filenames:
            file_path = os.path.join(sim_folder, os.path.basename(filename))
            print('writing to path: %s' % file_path)
            with open(file_path, 'wb') as outfile:
                outfile.write(data[filename])


if __name__ == '__main__':
    from idmtools.analysis.AnalyzeManager import AnalyzeManager
    from idmtools.core.PlatformFactory import PlatformFactory

    platform = PlatformFactory.create(key='COMPS')

    filenames = ['StdOut.txt']
    analyzers = [DownloadAnalyzer(filenames=filenames, output_path='download')]

    experiment_id = '31d83b39-85b4-e911-a2bb-f0921c167866'

    experiment = platform.get_item(id=experiment_id)

    manager = AnalyzeManager(configuration={}, platform=platform, items=experiment.children(), analyzers=analyzers)
    manager.analyze()
