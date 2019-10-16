from idmtools.analysis.AnalyzeManager import AnalyzeManager
from idmtools.analysis.AddAnalyzer import AddAnalyzer
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform

if __name__ == '__main__':

    platform = Platform('COMPS')

    filenames = ['StdOut.txt']
    analyzers = [AddAnalyzer(filenames=filenames)]

    experiment_id = '41e7edcc-02e6-e911-a2be-f0921c167861'

    manager = AnalyzeManager(platform=platform, ids=[(experiment_id, ItemType.EXPERIMENT)], analyzers=analyzers)
    manager.analyze()
