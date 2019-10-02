import os

from idmtools.entities.ianalyzer import IAnalyzer


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
        number = int(list(data.values())[0].split()[10])
        result = number + 100
        return result

    # ck4, should we pass objects as the keys? e.g. Item-type, not just their id
    def reduce(self, data):
        # data is currently a dict with item_id: value  entries
        value = sum(data.values())
        return value
