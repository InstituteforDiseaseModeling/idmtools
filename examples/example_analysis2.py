from idmtools.analysis.AnalyzeManager import AnalyzeManager
from idmtools.analysis.AddAnalyzer import AddAnalyzer
from idmtools.core.PlatformFactory import PlatformFactory


if __name__ == '__main__':

    platform = PlatformFactory.create(key='COMPS')

    filenames = ['StdOut.txt']
    analyzers = [AddAnalyzer(filenames=filenames)]

    experiment_id = '31d83b39-85b4-e911-a2bb-f0921c167866'

    experiment = platform.get_item(id=experiment_id)

    manager = AnalyzeManager(configuration={}, platform=platform, ids=[experiment.uid], analyzers=analyzers)
    manager.analyze()
