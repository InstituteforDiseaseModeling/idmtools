import copy
import typing
import uuid
from abc import ABC
from dataclasses import dataclass, field, InitVar

from more_itertools import grouper

from idmtools.core import EntityContainer, IAssetsEnabled, INamedEntity

if typing.TYPE_CHECKING:
    from idmtools.core.types import TSimulation, TSimulationClass, TCommandLine, TExperimentBuilder


@dataclass(repr=False)
class IExperiment(IAssetsEnabled, INamedEntity, ABC):
    """
    Represents a generic Experiment.
    This class needs to be implemented for each model type with specifics.

    Args:
        name: The experiment name.
        simulation_type: A class to initialize the simulations that will be created for this experiment
        assets: The asset collection for assets global to this experiment
        base_simulation: Optional a simulation that will be the base for all simulations created for this experiment
        command: Command to run on simulations
    """
    command: 'TCommandLine' = field(default=None)
    suite_id: uuid = field(default=None)
    base_simulation: 'TSimulation' = field(default=None)
    builder: 'TExperimentBuilder' = field(default=None, metadata={"pickle_ignore":True})
    simulation_type: 'InitVar[TSimulationClass]' = None
    simulations: 'EntityContainer' = field(default=None, compare=False)

    def __post_init__(self, simulation_type):
        super().__post_init__()
        self.simulations = EntityContainer()

        # Take care of the base simulation
        if not self.base_simulation:
            if simulation_type:
                self.base_simulation = simulation_type()
            else:
                raise Exception("A `base_simulation` or `simulation_type` needs to be provided to the Experiment object!")

        # Add a tag to keep the class name
        self.tags["type"] = self.__class__.__module__

    def __repr__(self):
        return f"<Experiment: {self.uid} - {self.name} / Sim count {len(self.simulations)}>"

    def display(self):
        from idmtools.utils.display import display, experiment_table_display
        display(self, experiment_table_display)

    def batch_simulations(self, batch_size=5):
        if not self.builder:
            yield (self.simulation(),)
            return

        for groups in grouper(self.builder, batch_size):
            sims = []
            for simulation_functions in filter(None, groups):
                simulation = self.simulation()
                tags = {}

                for func in simulation_functions:
                    new_tags = func(simulation=simulation)
                    if new_tags:
                        tags.update(new_tags)

                simulation.tags = tags
                sims.append(simulation)

            yield sims

    def simulation(self):
        """
        Returns a new simulation object.
        The simulation will be copied from the base simulation of the experiment.
        Returns: The created simulation
        """
        sim = copy.deepcopy(self.base_simulation)
        sim.experiment = self
        sim.assets = copy.deepcopy(self.base_simulation.assets)
        return sim

    def pre_creation(self):
        # Gather the assets
        self.gather_assets()

    def post_setstate(self):
        self.simulations = EntityContainer()

    @property
    def done(self):
        return all([s.done for s in self.simulations])

    @property
    def succeeded(self):
        return all([s.succeeded for s in self.simulations])

    @property
    def simulation_count(self):
        return len(self.simulations)
