"""
Defines our Simulation object.

The simulation object can be thought as a metadata object. It represents a configuration of a remote job execution metadata.
All simulations have a task. Optionally that have assets. All simulations should belong to an Experiment.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from dataclasses import dataclass, field, fields
from logging import getLogger, DEBUG
from typing import List, Union, Mapping, Any, Type, TypeVar, Dict, TYPE_CHECKING
from idmtools.assets import AssetCollection, Asset
from idmtools.core import ItemType, NoTaskFound
from idmtools.core.enums import EntityStatus
from idmtools.core.interfaces.iassets_enabled import IAssetsEnabled
from idmtools.core.interfaces.iitem import IItem
from idmtools.core.interfaces.inamed_entity import INamedEntity
from idmtools.entities.task_proxy import TaskProxy
from idmtools.utils.language import get_qualified_class_name_from_obj

if TYPE_CHECKING:  # pragma: no cover
    from idmtools.entities.itask import ITask
    from idmtools.entities.iplatform import IPlatform
    from idmtools.entities.experiment import Experiment

logger = getLogger(__name__)
user_logger = getLogger('user')


@dataclass
class Simulation(IAssetsEnabled, INamedEntity):
    """
    Class that represents a generic simulation.

    This class needs to be implemented for each model type with specifics.
    """
    #: Task representing the configuration of the command to be executed
    task: 'ITask' = field(default=None)  # noqa: F821
    #: Item Type. Should not be changed from Simulation
    item_type: ItemType = field(default=ItemType.SIMULATION, compare=False)
    #: Control whether we should replace the task with a proxy after creation
    __replace_task_with_proxy: bool = field(default=True, init=False, compare=False)
    #: Ensure we don't gather assets twice
    __assets_gathered: bool = field(default=False)
    #: Extra arguments to pass on creation to platform
    _platform_kwargs: dict = field(default_factory=dict)

    @property
    def experiment(self) -> 'Experiment':  # noqa: F821
        """
        Get experiment parent.

        Returns:
            Parent Experiment
        """
        return self.parent

    @experiment.setter
    def experiment(self, experiment: 'Experiment'):  # noqa: F821
        """
        Set the parent experiment.

        Args:
            experiment: Experiment to set as parent.

        Returns:
            None
        """
        self.parent = experiment

    def __repr__(self):
        """
        String representation of simulation.
        """
        return f"<Simulation: {self.uid} - Exp_id: {self.parent_id}>"

    def __hash__(self):
        """
        Hash of simulation(id).

        Returns:
            Hash of simulation
        """
        return id(self.uid)

    def pre_creation(self, platform: 'IPlatform'):
        """

        Runs before a simulation is created server side.

        Args:
            platform: Platform the item is being executed on

        Returns:
            None
        """
        # skip the IItem created function
        IItem.pre_creation(self, platform)
        if self.task is None:
            msg = 'Task is required for simulations'
            user_logger.error(msg)
            raise NoTaskFound(msg)

        if logger.isEnabledFor(DEBUG):
            logger.debug('Calling task pre creation')
        self.task.pre_creation(self, platform)

        self.gather_assets()

        if self.__class__ is not Simulation:
            # Add a tag to keep the Simulation class name
            sn = get_qualified_class_name_from_obj(self)
            if logger.isEnabledFor(DEBUG):
                logger.debug(f'Setting Simulation Tag "simulation_type" to "{sn}"')
            self.tags["simulation_type"] = sn

        # Add a tag to for task
        if self.task is not None:
            tn = get_qualified_class_name_from_obj(self.task)
            if logger.isEnabledFor(DEBUG):
                logger.debug(f'Setting Simulation Tag "task_type" to "{tn}"')
            self.tags["task_type"] = tn

    def post_creation(self, platform: 'IPlatform') -> None:
        """
        Called after a simulation is created.

        Args:
            platform: Platform simulation is being executed on

        Returns:
            None
        """
        if logger.isEnabledFor(DEBUG):
            logger.debug('Calling task post creation')
        if self.task is not None and not isinstance(self.task, TaskProxy):
            self.task.post_creation(self, self.platform)

        IItem.post_creation(self, platform)
        if self.__replace_task_with_proxy or (self.parent and self.parent._Experiment__replace_task_with_proxy):
            if logger.isEnabledFor(DEBUG):
                logger.debug('Replacing task with proxy')
            self.task = TaskProxy.from_task(self.task)
        if self.status is None:
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
        """
        Create a simulation from a task.

        Args:
            task: Task to create from
            tags: Tags to create on the simulation
            asset_collection: Simulation Assets

        Returns:
            Simulation using the  parameters provided
        """
        return Simulation(task=task, tags=dict() if tags is None else tags,
                          assets=asset_collection if asset_collection else AssetCollection())

    def list_static_assets(self, platform: 'IPlatform' = None, **kwargs) -> List[Asset]:
        """
        List assets that have been uploaded to a server already.

        Args:
            platform: Optional platform to load assets list from
            **kwargs:

        Returns:
            List of assets

        Raises:
            ValueError - If you try to list an assets for an simulation that hasn't been created/loaded from a remote platform.
        """
        if self.id is None:
            raise ValueError("You can only list static assets on an existing experiment")
        p = super()._check_for_platform_from_context(platform)
        return p._simulations.list_assets(self, **kwargs)

    def to_dict(self) -> Dict:
        """
        Do a lightweight conversation to json.

        Returns:
            Dict representing json of object
        """
        result = dict()
        for f in fields(self):
            if not f.name.startswith("_") and f.name not in ['parent']:
                result[f.name] = getattr(self, f.name)
        result['_uid'] = self.uid
        result['task'] = self.task.to_dict() if self.task else None
        return result


# TODO Rename to T simulation once old simulation is one
TTSimulation = TypeVar("TTSimulation", bound=Simulation)
TTSimulationClass = Type[TTSimulation]
TTSimulationBatch = List[TTSimulation]
TTAllSimulationData = Mapping[TTSimulation, Any]
TTSimulationList = List[Union[TTSimulation, str]]
