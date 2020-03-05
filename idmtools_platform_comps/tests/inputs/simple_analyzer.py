import json
import os

from idmtools.entities.ianalyzer import IAnalyzer as BaseAnalyzer


class SimpleAnalyzer(BaseAnalyzer):

    def __init__(self, filenames):
        super().__init__(filenames=filenames)

    def initialize(self):
        if not os.path.exists(os.path.join(self.working_dir, "output")):
            os.mkdir(os.path.join(self.working_dir, "output"))

    def map(self, data, simulation):
        return data['config.json']

    def reduce(self, all_data):
        output_dir = os.path.join(self.working_dir, "output")
        with open(os.path.join(output_dir, "aggregated_config.json"), "w") as fp:
            json.dump({str(s.uid): v for s, v in all_data.items()}, fp)
