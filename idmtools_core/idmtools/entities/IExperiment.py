import copy
from abc import ABCMeta

from idmtools.entities import ISimulation, CommandLine
from idmtools.assets.AssetCollection import AssetCollection
from idmtools.core import IEntity


class IExperiment(IEntity, metaclass=ABCMeta):
    """
    Represents a generic Experiment.
    This class needs to be implemented for each model type with specifics.
    """
    pickle_ignore_fields = ["builder"]

    def __init__(self, name, simulation_type: type, assets: AssetCollection = None,
                 base_simulation: ISimulation = None, command: CommandLine = None):
        """
        Constructor.
        Args:
            name: The experiment name.
            simulation_type: A class to initialize the simulations that will be created for this experiment
            assets: The asset collection for assets global to this experiment
            base_simulation: Optional a simulation that will be the base for all simulations created for this experiment
            command: Command to run on simulations
        """
        super().__init__()
        self.command = command or CommandLine()
        self.simulation_type = simulation_type
        self.simulations = []
        self.name = name
        self.base_simulation = base_simulation or self.simulation_type()
        self.builder = None
        self.suite_id = None
        self.assets = assets or AssetCollection()

    def __repr__(self):
        return f"<Experiment: {self.uid} - {self.name} / Sim count {len(self.simulations)}>"

    def execute_builder(self):
        """
        Execute the builder of this experiment, generating all the simulations.
        """
        for simulation_functions in self.builder:
            simulation = self.simulation()
            tags = {}

            for func in simulation_functions:
                tags.update(func(simulation=simulation))

            simulation.tags = tags

    def simulation(self):
        """
        Returns a new simulation object.
        The simulation will be copied from the base simulation of the experiment.
        Returns: The created simulation
        """
        sim = copy.deepcopy(self.base_simulation)

        sim.experiment_id = self.uid
        self.simulations.append(sim)
        sim.experiment = self
        return sim

