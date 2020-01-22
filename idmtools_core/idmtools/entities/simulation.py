from logging import getLogger
from typing import List, Callable, NoReturn, Union, Mapping, Any, Type, TypeVar
from dataclasses import dataclass, field
from idmtools.core import ItemType, NoTaskFound
from idmtools.core.interfaces.iassets_enabled import IAssetsEnabled
from idmtools.core.interfaces.inamed_entity import INamedEntity


logger = getLogger(__name__)
user_logger = getLogger('user')


@dataclass
class Simulation(IAssetsEnabled, INamedEntity):
    """
    Class that represents a generic simulation.
    This class needs to be implemented for each model type with specifics.
    """
    task: 'ITask' = field(default_factory=None)
    item_type: 'ItemType' = field(default=ItemType.SIMULATION, compare=False)
    pre_creation_hooks: List[Callable[[], NoReturn]] = field(default_factory=lambda: [Simulation.gather_assets])

    @property
    def experiment(self) -> 'Experiment':
        return self.parent

    @experiment.setter
    def experiment(self, experiment: 'Experiment'):
        self.parent = experiment

    def __repr__(self):
        return f"<Simulation: {self.uid} - Exp_id: {self.parent_id}>"

    def __hash__(self):
        return id(self.uid)

    def pre_creation(self):
        # Call all of our hooks
        [x(self) for x in self.pre_creation_hooks]
        if self.__class__ is not Simulation:
            # Add a tag to keep the Simulation class name
            self.tags["experiment_type"] = f'{self.__class__.__module__}.{self.__class__.__name__}'
            self.tags["simulation_type"] = f'{self.__class__.__module__}.{self.__class__.__name__}'

        if self.task is None:
            msg = 'Task is required for simulations'
            user_logger.error(msg)
            raise NoTaskFound(msg)

        # Add a tag to keep the Simulation class name
        self.tags["task_type"] = f'{self.task.__class__.__module__}.{self.task.__class__.__name__}'

    def pre_getstate(self):
        """
        Return default values for :meth:`pickle_ignore_fields`. Call before pickling.
        """
        from idmtools.assets import AssetCollection
        from idmtools.core.interfaces.entity_container import EntityContainer
        return {"assets": AssetCollection(), "simulations": EntityContainer()}

    def gather_assets(self):
        """
        Gather all the assets for the simulation.
        """
        self.task.gather_transient_assets()
        self.assets.add_assets(self.task.transient_assets)


# TODO Rename to T simulation once old simulation is one
TTSimulation = TypeVar("TTSimulation", bound=Simulation)
TTSimulationClass = Type[TTSimulation]
TTSimulationBatch = List[TTSimulation]
TTAllSimulationData = Mapping[TTSimulation, Any]
TTSimulationList = List[Union[TTSimulation, str]]
