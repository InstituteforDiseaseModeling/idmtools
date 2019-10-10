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
from idmtools.entities.icontainer_item import IContainerItem

if typing.TYPE_CHECKING:
    from idmtools.core.types import TSimulation, TSimulationClass, TExperimentBuilder
    from idmtools.entities.command_line import TCommandLine


@dataclass(repr=False)
class IExperiment(IAssetsEnabled, IContainerItem, INamedEntity, ABC):
    """
    Represents a generic Experiment.
    This class needs to be implemented for each model type with specifics.

    Args:
        command: The command to run for experiment
        suite_id: Suite Id for the experiment
        simulation_type: A typpe of simulation
        base_simulation: Optional a simulation that will be the base for all simulations created for this experiment
        builders: A set of Experiment Builders to be used to generate simulations
        simulations: Optional a user input simulations
    """
    command: 'TCommandLine' = field(default=None)
    suite_id: uuid = field(default=None)
    simulation_type: 'InitVar[TSimulationClass]' = None
    base_simulation: 'TSimulation' = field(default=None, compare=False, metadata={"pickle_ignore": True})
    builders: set = field(default_factory=lambda: set(), compare=False, metadata={"pickle_ignore": True})
    simulations: EntityContainer = field(default_factory=lambda: EntityContainer(), compare=False,
                                         metadata={"pickle_ignore": True})

    # @property
    # def simulations(self):
    #     return self.children(refresh=False)

    def __post_init__(self, simulation_type):
        super().__post_init__()
        self.simulations = self.simulations or EntityContainer()
        # Take care of the base simulation
        if not self.base_simulation:
            if simulation_type and callable(simulation_type):
                self.base_simulation = simulation_type()
            else:
                raise Exception(
                    "A `base_simulation` or `simulation_type` needs to be provided to the Experiment object!")

        self._simulation_default = self.base_simulation.__class__()

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
        sim.assets = copy.deepcopy(self.base_simulation.assets)
        sim.platform = self.platform
        sim.parent_id = self.uid
        return sim

    def pre_creation(self):
        # Gather the assets
        self.gather_assets()

        # Add a tag to keep the class name
        self.tags["type"] = f'{self.__class__.__module__}.{self.__class__.__name__}'

    @property
    def done(self):
        return all([s.done for s in self.children()])

    @property
    def succeeded(self):
        return all([s.succeeded for s in self.children()])

    @property
    def simulation_count(self):
        return len(self.children())

    def pre_getstate(self):
        """
        Function called before picking
        Return default values for "pickle-ignore" fields
        """
        from idmtools.assets import AssetCollection
        return {"assets": AssetCollection(), "simulations": EntityContainer(), "builders": set(),
                "base_simulation": self._simulation_default}


TExperiment = typing.TypeVar("TExperiment", bound=IExperiment)
TExperimentClass = typing.Type[TExperiment]
# Composed types
TExperimentList = typing.List[typing.Union[TExperiment, str]]
