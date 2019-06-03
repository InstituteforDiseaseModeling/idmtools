from typing import List, Union

from idmtools.analysis import IAnalyzer
from idmtools.entities import IExperiment


class AnalyzeManager:

    def __init__(self, experiments: List[Union[IExperiment, str]], analyzers=List[IAnalyzer]):
        self.experiments = experiments
        self.analyzers = analyzers

    def analyze(self):
        print("Analysis")