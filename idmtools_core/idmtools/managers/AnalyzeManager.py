import typing

if typing.TYPE_CHECKING:
    from idmtools.core.types import TExperimentsList, TAnalyzerList


class AnalyzeManager:

    def __init__(self, experiments: 'TExperimentsList', analyzers: 'TAnalyzerList'):
        self.experiments = experiments
        self.analyzers = analyzers

    def analyze(self):
        print("Analysis")