import os

from idmtools.entities.IAnalyzer import IAnalyzer


class AddAnalyzer(IAnalyzer):
    """
    Add Analyzer
    A simple base class to add analyzers.

    """
    def __init__(self, filenames=None, output_path='output'):
        super().__init__()
        self.output_path = output_path
        self.filenames = filenames or []

        # We only want the raw files -> disable parsing
        self.parse = True

    def filter(self, item):
        return True  # download them all!

    def initialize(self):
        self.output_path = os.path.join(self.working_dir, self.output_path)
        os.makedirs(self.output_path, exist_ok=True)

    def map(self, data, item):
        number = int(list(data.values())[0].split()[0])
        result = number + 100
        return result

    # ck4, should we pass objects as the keys? e.g. Item-type, not just their id
    def reduce(self, data):
        # data is currently a dict with item_id: value  entries
        value = sum(data.values())
        return value


if __name__ == '__main__':
    from idmtools.analysis.AnalyzeManager import AnalyzeManager
    from idmtools.core.PlatformFactory import PlatformFactory

    platform = PlatformFactory.create(key='COMPS')

    filenames = ['StdOut.txt']
    analyzers = [AddAnalyzer(filenames=filenames)]

    obj_id = '31d83b39-85b4-e911-a2bb-f0921c167866'

    obj = platform.get_item(id=obj_id, level=1)
    obj.children = platform.get_objects_by_relationship(object=obj, relationship=platform.CHILD)

    manager = AnalyzeManager(configuration={}, platform=platform, items=obj.children, analyzers=analyzers)
    manager.analyze()
