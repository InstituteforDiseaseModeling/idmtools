import typing

from idmtools.utils.entities import retrieve_experiment

if typing.TYPE_CHECKING:
    from idmtools.entities.iexperiment import TExperimentList
    from idmtools.entities.ianalyzer import TAnalyzerList


class AnalyzeManager:

    def __init__(self, experiments: 'TExperimentList', analyzers: 'TAnalyzerList', platform):
        self.experiments = [retrieve_experiment(e, platform, True) for e in experiments]
        self.analyzers = analyzers
        self.platform = platform

    def analyze(self):
        # Run the per experiment on the analyzers
        for exp in self.experiments:
            for a in self.analyzers:
                a.per_experiment(exp)

        # Collect the simulations
        simulations = []
        for exp in self.experiments:
            simulations.extend([s for s in exp.simulations if s not in simulations])

        # filter
        analyzers_sims = {a: [s for s in simulations if a.filter(s)] for a in self.analyzers}

        print(analyzers_sims)
