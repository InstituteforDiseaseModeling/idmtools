from idmtools.analysis.AnalyzeManager import AnalyzeManager
from idmtools.analysis.DownloadAnalyzer import DownloadAnalyzer
from idmtools.core.platform_factory import Platform

if __name__ == '__main__':

    platform = Platform('COMPS')

    filenames = ['StdOut.txt']
    analyzers = [DownloadAnalyzer(filenames=filenames, output_path='download')]

    experiment_id = '11052582-83da-e911-a2be-f0921c167861'

    manager = AnalyzeManager(configuration={}, platform=platform, ids=[experiment_id], analyzers=analyzers)
    manager.analyze()
