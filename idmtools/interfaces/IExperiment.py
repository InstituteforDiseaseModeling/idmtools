import copy

from interfaces.IEntity import IEntity
from interfaces.ISimulation import ISimulation


class IExperiment(IEntity):
    """
    Represents a generic Simulation.
    This class needs to be implemented for each model type with specifics.
    """

    def __init__(self, name, simulation_type: type, assets=None, base_simulation: ISimulation = None):
        super().__init__(assets=assets)
        self.simulation_type = simulation_type
        self.simulations = []
        self.name = name
        self.base_simulation = base_simulation or self.simulation_type()
        self.builder = None

    def __repr__(self):
        return f"<Experiment: {self.uid} - {self.name} / Sim count {len(self.simulations)}>"

    def execute_builder(self):
        for simulation_functions in self.builder:
            simulation = self.simulation()
            tags = {}

            for func in simulation_functions:
                tags.update(func(simulation=simulation))

    def simulation(self, **kwargs):
        if not self.base_simulation:
            sim = self.simulation_type(**kwargs)
        else:
            sim = copy.deepcopy(self.base_simulation)

        sim.experiment_id = self.uid
        self.simulations.append(sim)
        return sim
