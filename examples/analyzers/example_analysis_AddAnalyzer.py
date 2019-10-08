from idmtools.analysis.AnalyzeManager import AnalyzeManager
from idmtools.analysis.AddAnalyzer import AddAnalyzer
from idmtools.core.platform_factory import Platform

if __name__ == '__main__':

    platform = Platform('COMPS')

    filenames = ['StdOut.txt']
    analyzers = [AddAnalyzer(filenames=filenames)]

    experiment_id = '41e7edcc-02e6-e911-a2be-f0921c167861'

    experiment = platform.get_item(id=experiment_id)

    manager = AnalyzeManager(platform=platform, ids=[experiment.uid], analyzers=analyzers)
    manager.analyze()
