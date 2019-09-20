import copy
import typing
import uuid
from abc import ABC
from itertools import chain
from dataclasses import dataclass, field, InitVar
from more_itertools import grouper
from idmtools.core.interfaces.entity_container import EntityContainer
from idmtools.core.interfaces.iassets_enabled import IAssetsEnabled
from idmtools.core.interfaces.inamed_entity import INamedEntity

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
    simulation_type: 'InitVar[TSimulationClass]' = None
    builders: set = field(default=None, compare=False, metadata={"pickle_ignore": True})
    simulations: 'EntityContainer' = field(default=None, compare=False, metadata={"pickle_ignore": True})

    def __post_init__(self, simulation_type):
        super().__post_init__()
        self.simulations = EntityContainer()
        # Take care of the base simulation
        if not self.base_simulation:
            if simulation_type and callable(simulation_type):
                self.base_simulation = simulation_type()
            else:
                raise Exception(
                    "A `base_simulation` or `simulation_type` needs to be provided to the Experiment object!")

    def __repr__(self):
        return f"<Experiment: {self.uid} - {self.name} / Sim count {len(self.simulations) if self.simulations else 0}>"

    @property
    def builder(self) -> 'TExperimentBuilder':
        """
        For back-compatibility purpose
        Returns: the last 'TExperimentBuilder'
        """
        return list(self.builders)[-1] if self.builders and len(self.builders) > 0 else None

    @builder.setter
    def builder(self, builder: 'TExperimentBuilder') -> None:
        """
        For back-compatibility purpose
        Args:
            builder: new builder to be used
        Returns: None
        """

        # Make sure we only take the last builder assignment
        if self.builders:
            self.builders.clear()

        self.add_builder(builder)

    def add_builder(self, builder: 'TExperimentBuilder') -> None:
        """
        Add builder to builder collection
        Args:
            builder: a builder to be added
        Returns: None
        """
        from idmtools.builders import ExperimentBuilder

        # Add builder validation
        if not isinstance(builder, ExperimentBuilder):
            raise Exception("Builder ({}) must have type of ExperimentBuilder!".format(builder))

        # Initialize builders the first time
        if self.builders is None:
            self.builders = set()

        # Add new builder to the collection
        self.builders.add(builder)

    def display(self):
        from idmtools.utils.display import display, experiment_table_display
        display(self, experiment_table_display)

    def batch_simulations(self, batch_size=5):
        if not self.builders:
            yield (self.simulation(),)
            return

        for groups in grouper(chain(*self.builders), batch_size):
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

        # Add a tag to keep the class name
        self.tags["type"] = f'{self.__class__.__module__}.{self.__class__.__name__}'

    @property
    def done(self):
        return all([s.done for s in self.simulations])

    @property
    def succeeded(self):
        return all([s.succeeded for s in self.simulations])

    @property
    def simulation_count(self):
        return len(self.simulations)

    def post_setstate(self):
        """
        Function called after restoring the state if additional initialization is required
        """
        if self.simulations is None:
            self.simulations = EntityContainer()


TExperiment = typing.TypeVar("TExperiment", bound=IExperiment)
TExperimentClass = typing.Type[TExperiment]
# Composed types
TExperimentsList = typing.List[typing.Union[TExperiment, str]]
