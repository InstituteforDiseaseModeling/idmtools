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
        # make sure these not overridden
        parent_id = getattr(simulation, 'parent_id')
        children_ids = getattr(simulation, 'children_ids')

        simulation.__dict__ = simulation_to_set.__dict__

        simulation.parent_id = parent_id
        simulation.children_ids = children_ids
        return {}

    def __iter__(self):
        for simulation in self.simulations:
            yield [partial(StandAloneSimulationsBuilder.set_simulation, simulation_to_set=simulation)]
