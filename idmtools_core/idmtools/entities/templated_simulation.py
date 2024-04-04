"""
TemplatedSimulations provides a utility to build sets of simulations from a base simulation.

This is meant to be combined with builders.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import copy
from dataclasses import dataclass, field, fields, InitVar
from functools import partial
from itertools import chain
from typing import Set, Generator, Dict, Any, List, TYPE_CHECKING
from more_itertools import grouper
from idmtools.builders.simulation_builder import SimulationBuilder
from idmtools.entities.itask import ITask
from idmtools.entities.simulation import Simulation
from idmtools.utils.collections import ResetGenerator
from idmtools.utils.hashing import ignore_fields_in_dataclass_on_pickle

if TYPE_CHECKING:  # pragma: no cover
    from idmtools.entities.experiment import Experiment


def simulation_generator(builders, new_sim_func, additional_sims=None, batch_size=10):
    """
    Generates batches of simulations from the templated simulations.

    Args:
        builders: List of builders to build
        new_sim_func: Build new simulation callback
        additional_sims: Additional simulations
        batch_size: Batch size

    Returns:
        Generator for simulations in batches
    """
    if additional_sims is None:
        additional_sims = []
    # Then the builders
    for groups in grouper(chain(*builders), batch_size):
        for simulation_functions in filter(None, groups):
            simulation = new_sim_func()
            tags = {}

            for func in simulation_functions:
                new_tags = func(simulation=simulation)
                if new_tags:
                    tags.update(new_tags)

            simulation.tags.update(tags)
            yield simulation

    yield from additional_sims


@dataclass(repr=False)
class TemplatedSimulations:
    """
    Class for building templated simulations and commonly used with SimulationBuilder class.

    Examples:
        Add tags to all simulations via base task::

            ts = TemplatedSimulations(base_task=task)
            ts.tags = {'a': 'test', 'b': 9}
            ts.add_builder(builder)

        Add tags to a specific simulation::

            experiment =  Experiment.from_builder(builder, task, name=expname)
            experiment.simulations = list(experiment.simulations)
            experiment.simulations[2].tags['test']=123
    """
    builders: Set[SimulationBuilder] = field(default_factory=set, compare=False)
    base_simulation: Simulation = field(default=None, compare=False, metadata={"pickle_ignore": True})
    base_task: ITask = field(default=None)
    parent: 'Experiment' = field(default=None)
    tags: InitVar[Dict] = None
    __extra_simulations: List[Simulation] = field(default_factory=list)

    def __post_init__(self, tags):
        """
        Constructor.

        Args:
            tags: Tags to set on the base simulation

        Returns:
            None

        Raises:
            ValueError - If base task is not set, and base simulations is not set or bas_simulation_task is not set.
        """
        if self.base_task is None and (self.base_simulation is None or self.base_simulation.task is None):
            raise ValueError("Either a base simulation or a base_task are required")

        if self.base_simulation is None:
            self.base_simulation = Simulation(task=self.base_task)
        else:
            self.base_task = self.base_simulation.task

        if tags and not isinstance(tags, property):
            self.base_simulation.tags.update(tags)

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

        Raises:
            ValueError - Builder must be type of SimulationBuilder
        """
        from idmtools.builders import SimulationBuilder, ArmSimulationBuilder

        # Add builder validation
        if not isinstance(builder, (SimulationBuilder, ArmSimulationBuilder)):
            raise ValueError("Builder ({}) must have type of ExperimentBuilder!".format(builder))

        # Initialize builders the first time
        if self.builders is None:
            self.builders = set()

        # Add new builder to the collection
        self.builders.add(builder)

    @property
    def pickle_ignore_fields(self):
        """
        Fields that we should ignore on the object.

        Returns:
            Fields to ignore
        """
        return set(f.name for f in fields(self) if "pickle_ignore" in f.metadata and f.metadata["pickle_ignore"])

    def display(self):
        """
        Display the templated simulation.

        Returns:
            None
        """
        from idmtools.utils.display import display, experiment_table_display
        display(self, experiment_table_display)

    def simulations(self) -> Generator[Simulation, None, None]:
        """
        Simulations iterator.

        Returns:
            Simulation iterator
        """
        p = partial(simulation_generator, self.builders, self.new_simulation, self.__extra_simulations)
        return ResetGenerator(p)

    def extra_simulations(self) -> List[Simulation]:
        """
        Returns the extra simulations defined on template.

        Returns:
            Returns the extra simulations defined
        """
        return self.__extra_simulations

    def add_simulation(self, simulation: Simulation):
        """
        Add a simulation that was built outside template engine to template generator.

        This is useful we you can build most simulations through a template but need a some that cannot. This is especially true
        for large simulation sets.

        Args:
            simulation: Simulation to add

        Returns:
            None
        """
        self.__extra_simulations.append(simulation)

    def add_simulations(self, simulations: List[Simulation]):
        """
        Add multiple simulations without templating. See add_simulation.

        Args:
            simulations: Simulation to add

        Returns:
            None
        """
        self.__extra_simulations.extend(simulations)

    def new_simulation(self):
        """
        Return a new simulation object.

        The simulation will be copied from the base simulation of the experiment.

        Returns:
            The created simulation.
        """
        # TODO: the experiment should be frozen when the first simulation is created
        sim = copy.deepcopy(self.base_simulation)
        # Set UID=none to ensure it is regenerated
        sim._uid = None
        sim.assets = copy.deepcopy(self.base_simulation.assets)
        sim.parent = self.parent
        return sim

    @property
    def tags(self):
        """
        Get tags for the base simulation.

        Returns:
            Tags for base simulation
        """
        return self.base_simulation.tags

    @tags.setter
    def tags(self, tags):
        """
        Set tags on the base simulation.

        Args:
            tags: Tags to set

        Returns:
            None
        """
        self.base_simulation.tags = tags

    def __iter__(self):
        """
        Iterator over the simulations.

        Returns:
            Simulations itero
        """
        return self.simulations()

    def __getstate__(self):
        """
        Ignore the fields in pickle_ignore_fields during pickling.
        """
        return ignore_fields_in_dataclass_on_pickle(self)

    def __setstate__(self, state):
        """
        Add ignored fields back since they don't exist in the pickle.
        """
        self.__dict__.update(state)

    def __len__(self):
        """
        Length of the templated simulations.

        Returns:
            Total number of simulations
        """
        return sum([len(b) for b in self.builders]) + len(self.__extra_simulations)

    @classmethod
    def from_task(cls, task: ITask, tags: Dict[str, Any] = None) -> 'TemplatedSimulations':
        """
        Creates a templated simulation from a task.

        We use the task to set as base_task, and the tags are applied to the base simulation we need internally.

        Args:
            task: Task to use as base task
            tags: Tags to add to base simulation

        Returns:
            TemplatedSimulations from the task
        """
        return TemplatedSimulations(base_task=task, tags=tags)
