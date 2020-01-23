import copy
from itertools import chain
from typing import Set
from uuid import UUID
from dataclasses import dataclass, field

from more_itertools import grouper
from idmtools.core.enums import ItemType
from idmtools.builders.experiment_builder import ExperimentBuilder
from idmtools.core.interfaces.entity_container import EntityContainer
from idmtools.core.interfaces.iassets_enabled import IAssetsEnabled
from idmtools.core.interfaces.inamed_entity import INamedEntity
from idmtools.entities.itask import ITask
from idmtools.entities.platform_requirements import PlatformRequirements
from idmtools.entities.simulation import Simulation


@dataclass(repr=False)
class TemplatedExperiment(IAssetsEnabled, INamedEntity):
    base_task: ITask = field(default=None)
    suite_id: UUID = field(default=None)
    simulations: EntityContainer = field(default_factory=lambda: EntityContainer(), compare=False,
                                         metadata={"pickle_ignore": True})
    item_type: ItemType = field(default=ItemType.EXPERIMENT, compare=False, init=False)
    task_type: str = field(default=None, init=False)
    platform_requirements: Set[PlatformRequirements] = field(default_factory=set)
    base_simulation: Simulation = field(default=None, compare=False, metadata={"pickle_ignore": True})
    builders: set = field(default_factory=lambda: set(), compare=False, metadata={"pickle_ignore": True})

    def __post_init__(self):
        if self.base_task and (self.base_simulation is None or
                               (self.base_simulation and self.base_simulation.task is None)):
            raise ValueError("Either the base task or base simulation with a task defined is required")

        if self.base_task:
            self.base_simulation = Simulation(task=self.base_task)
        elif self.base_simulation:
            self.base_task = self.base_simulation.task
        self.task_type = f'{self.base_simulation.task.__module__}.{self.base_simulation.task.__class__}'

    @property
    def suite(self):
        return self.parent

    @suite.setter
    def suite(self, suite):
        self.parent = suite

    @property
    def builder(self) -> ExperimentBuilder:

        """
        For backward-compatibility purposes.

        Returns:
            The last ``TExperimentBuilder``.
        """
        return list(self.builders)[-1] if self.builders and len(self.builders) > 0 else None

    @builder.setter
    def builder(self, builder: ExperimentBuilder) -> None:
        """
        For backward-compatibility purposes.

        Args:
            builder: The new builder to be used.

        Returns:
            None
        """

        # Make sure we only take the last builder assignment
        if self.builders:
            self.builders.clear()

        self.add_builder(builder)

    def add_builder(self, builder: ExperimentBuilder) -> None:
        """
        Add builder to builder collection.

        Args:
            builder: A builder to be added.

        Returns:
            None
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
        # If no builders and no simulation, just return the base simulation
        if not self.builders and not self.simulations:
            yield (self.new_simulation(),)
            return

        # First consider the simulations of the experiment
        if self.simulations:
            for sim in self.simulations:
                sim.platform = self.platform
                sim.experiment = self

            for groups in grouper(self.simulations, batch_size):
                sims = []
                for sim in filter(None, groups):
                    sims.append(sim)
                yield sims

        # Then the builders
        for groups in grouper(chain(*self.builders), batch_size):
            sims = []
            for simulation_functions in filter(None, groups):
                simulation = self.new_simulation()
                tags = {}

                for func in simulation_functions:
                    new_tags = func(simulation=simulation)
                    if new_tags:
                        tags.update(new_tags)

                simulation.tags.update(tags)
                sims.append(simulation)

            yield sims

    def new_simulation(self):
        """
        Return a new simulation object.
        The simulation will be copied from the base simulation of the experiment.

        Returns:
            The created simulation.
        """
        # TODO: the experiment should be frozen when the first simulation is created
        sim = copy.deepcopy(self.base_simulation)
        sim.assets = copy.deepcopy(self.base_simulation.assets)
        sim.platform = self.platform
        sim.experiment = self
        return sim

    def pre_getstate(self):
        """
        Return default values for :meth:`~idmtools.interfaces.ientity.pickle_ignore_fields`.
        Call before pickling.
        """
        from idmtools.assets import AssetCollection
        return {"assets": AssetCollection(), "simulations": EntityContainer(), "builders": set(),
                "base_simulation": self.base_simulation}
