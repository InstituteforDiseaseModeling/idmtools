from dataclasses import dataclass, field
from logging import getLogger, DEBUG
from typing import List, Callable, NoReturn, Union, Mapping, Any, Type, TypeVar, Dict

from idmtools.assets import AssetCollection
from idmtools.core import ItemType, NoTaskFound
from idmtools.core.enums import EntityStatus
from idmtools.core.interfaces.iassets_enabled import IAssetsEnabled
from idmtools.core.interfaces.inamed_entity import INamedEntity
from idmtools.entities.task_proxy import TaskProxy
from idmtools.utils.language import get_qualified_class_name_from_obj

logger = getLogger(__name__)
user_logger = getLogger('user')


@dataclass
class Simulation(IAssetsEnabled, INamedEntity):
    """
    Class that represents a generic simulation.
    This class needs to be implemented for each model type with specifics.
    """
    task: 'ITask' = field(default=None)  # noqa: F821
    item_type: 'ItemType' = field(default=ItemType.SIMULATION, compare=False)
    pre_creation_hooks: List[Callable[[], NoReturn]] = field(default_factory=lambda: [Simulation.gather_assets])
    # control whether we should replace the task with a proxy after creation
    __replace_task_with_proxy: bool = field(default=True, init=False, compare=False)
    # Ensure we don't gather assets twice
    __assets_gathered: bool = field(default=False)

    @property
    def experiment(self) -> 'Experiment':  # noqa: F821
        return self.parent

    @experiment.setter
    def experiment(self, experiment: 'Experiment'):  # noqa: F821
        self.parent = experiment

    def __repr__(self):
        return f"<Simulation: {self.uid} - Exp_id: {self.parent_id}>"

    def __hash__(self):
        return id(self.uid)

    def pre_creation(self):
        if self.task is None:
            msg = 'Task is required for simulations'
            user_logger.error(msg)
            raise NoTaskFound(msg)

        if logger.isEnabledFor(DEBUG):
            logger.debug('Calling task pre creation')
        self.task.pre_creation(self)

        # Call all of our hooks
        for x in self.pre_creation_hooks:
            if logger.isEnabledFor(DEBUG):
                logger.debug(f'Calling simulation pre-create hook named '
                             f'{x.__name__ if hasattr(x, "__name__") else str(x)}')
            x(self)

        if self.__class__ is not Simulation:
            # Add a tag to keep the Simulation class name
            sn = get_qualified_class_name_from_obj(self)
            if logger.isEnabledFor(DEBUG):
                logger.debug(f'Setting Simulation Tag "simulation_type" to "{sn}"')
            self.tags["simulation_type"] = sn

        # Add a tag to for task
        if self.parent is None or "task_type" not in self.parent.tags:
            tn = get_qualified_class_name_from_obj(self.task)
            if logger.isEnabledFor(DEBUG):
                logger.debug(f'Setting Simulation Tag "task_type" to "{tn}"')
            self.tags["task_type"] = tn

    def post_creation(self) -> None:
        if logger.isEnabledFor(DEBUG):
            logger.debug('Calling task post creation')
        if self.task is not None and not isinstance(self.task, TaskProxy):
            self.task.post_creation(self)

        if self.__replace_task_with_proxy or (self.parent and self.parent._Experiment__replace_task_with_proxy):
            if logger.isEnabledFor(DEBUG):
                logger.debug('Replacing task with proxy')
            self.task = TaskProxy.from_task(self.task)
        self.status = EntityStatus.CREATED

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
        if not self.__assets_gathered:
            self.task.gather_transient_assets()
            self.assets.add_assets(self.task.transient_assets, fail_on_duplicate=False)
        self.__assets_gathered = True

    @classmethod
    def from_task(cls, task: 'ITask', tags: Dict[str, Any] = None,  # noqa E821
                  asset_collection: AssetCollection = None):
        return Simulation(task=task, tags=dict() if tags is None else tags,
                          assets=asset_collection if asset_collection else AssetCollection())


# TODO Rename to T simulation once old simulation is one
TTSimulation = TypeVar("TTSimulation", bound=Simulation)
TTSimulationClass = Type[TTSimulation]
TTSimulationBatch = List[TTSimulation]
TTAllSimulationData = Mapping[TTSimulation, Any]
TTSimulationList = List[Union[TTSimulation, str]]
