from idmtools.analysis.AnalyzeManager import AnalyzeManager
from idmtools.analysis.DownloadAnalyzer import DownloadAnalyzer
from idmtools.core.PlatformFactory import PlatformFactory

if __name__ == '__main__':

    platform = PlatformFactory.create(key='COMPS')

    filenames = ['StdOut.txt']
    analyzers = [DownloadAnalyzer(filenames=filenames, output_path='download')]

    experiment_id = '31d83b39-85b4-e911-a2bb-f0921c167866'

    manager = AnalyzeManager(configuration={}, platform=platform, ids=[experiment_id], analyzers=analyzers)
    manager.analyze()
