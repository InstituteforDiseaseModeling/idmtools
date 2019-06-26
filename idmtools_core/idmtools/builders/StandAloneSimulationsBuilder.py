from functools import partial

from idmtools.builders import ExperimentBuilder


class StandAloneSimulationsBuilder(ExperimentBuilder):
    def __init__(self):
        super().__init__()
        self.simulations = []

    def add_simulation(self, simulation):
        self.simulations.append(simulation)

    @staticmethod
    def set_simulation(simulation, simulation_to_set):
        simulation.__dict__ = simulation_to_set.__dict__
        return {}

    def __iter__(self):
        for simulation in self.simulations:
            yield [partial(StandAloneSimulationsBuilder.set_simulation, simulation_to_set=simulation)]
