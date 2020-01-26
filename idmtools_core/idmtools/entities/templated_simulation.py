import copy
from dataclasses import dataclass, field, fields
from itertools import chain
from typing import Set, Generator
from more_itertools import grouper
from idmtools.builders.simulation_builder import SimulationBuilder
from idmtools.entities.itask import ITask
from idmtools.entities.simulation import Simulation
from idmtools.utils.hashing import ignore_fields_in_dataclass_on_pickle


@dataclass(repr=False)
class TemplatedSimulations:
    builders: Set[SimulationBuilder] = field(default_factory=lambda: set(), compare=False)
    base_simulation: Simulation = field(default=None, compare=False, metadata={"pickle_ignore": True})
    base_task: ITask = field(default=None)

    def __post_init__(self):
        if self.base_task is None and (self.base_simulation is None or self.base_simulation.task is None):
            raise ValueError("Either a base simulation or a base_task are required")

        if self.base_simulation is None:
            self.base_simulation = Simulation(task=self.base_task)
        else:
            self.base_task = self.base_simulation.task

    @property
    def builder(self) -> SimulationBuilder:

        """
        For backward-compatibility purposes.

        Returns:
            The last ``TExperimentBuilder``.
        """
        return list(self.builders)[-1] if self.builders and len(self.builders) > 0 else None

    @builder.setter
    def builder(self, builder: SimulationBuilder) -> None:
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

    def add_builder(self, builder: SimulationBuilder) -> None:
        """
        Add builder to builder collection.

        Args:
            builder: A builder to be added.

        Returns:
            None
        """
        from idmtools.builders import SimulationBuilder

        # Add builder validation
        if not isinstance(builder, SimulationBuilder):
            raise Exception("Builder ({}) must have type of ExperimentBuilder!".format(builder))

        # Initialize builders the first time
        if self.builders is None:
            self.builders = set()

        # Add new builder to the collection
        self.builders.add(builder)

    @property
    def pickle_ignore_fields(self):
        return set(f.name for f in fields(self) if "pickle_ignore" in f.metadata and f.metadata["pickle_ignore"])

    def display(self):
        from idmtools.utils.display import display, experiment_table_display
        display(self, experiment_table_display)

    def simulations(self) -> Generator[Simulation, None, None]:
        # Then the builders
        for groups in grouper(chain(*self.builders), 100):
            for simulation_functions in filter(None, groups):
                simulation = self.new_simulation()
                tags = {}

                for func in simulation_functions:
                    new_tags = func(simulation=simulation)
                    if new_tags:
                        tags.update(new_tags)

                simulation.tags.update(tags)
                yield simulation

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
        return sim

    def __iter__(self):
        return self.simulations()

    def __getstate__(self):
        """
        Ignore the fields in pickle_ignore_fields during pickling.
        """
        return ignore_fields_in_dataclass_on_pickle(self)

    def __setstate__(self, state):
        """
        Add ignored fields back since they don't exist in the pickle
        """
        self.__dict__.update(state)
