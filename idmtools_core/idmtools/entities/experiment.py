import copy
import uuid
from dataclasses import dataclass, field, InitVar
from logging import getLogger
from types import GeneratorType
from typing import NoReturn, Set, Union, Iterator, Type, Dict, Any, List

from idmtools import __version__
from idmtools.assets import AssetCollection
from idmtools.core import ItemType
from idmtools.core.interfaces.entity_container import EntityContainer
from idmtools.core.interfaces.iassets_enabled import IAssetsEnabled
from idmtools.core.interfaces.inamed_entity import INamedEntity
from idmtools.entities.itask import ITask
from idmtools.entities.platform_requirements import PlatformRequirements
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools.registry.experiment_specification import ExperimentPluginSpecification, get_model_impl, \
    get_model_type_impl
from idmtools.registry.plugin_specification import get_description_impl
from idmtools.utils.collections import ParentIterator

logger = getLogger(__name__)

SUPPORTED_SIM_TYPE = Union[EntityContainer, GeneratorType, TemplatedSimulations, Iterator]


@dataclass(repr=False)
class Experiment(IAssetsEnabled, INamedEntity):
    """
    Class that represents a generic experiment.
    This class needs to be implemented for each model type with specifics.

    Args:
        name: The experiment name.
        assets: The asset collection for assets global to this experiment.
    """
    suite_id: uuid = field(default=None)

    item_type: ItemType = field(default=ItemType.EXPERIMENT, compare=False, init=False)
    task_type: str = field(default='idmtools.entities.command_task.CommandTask')
    platform_requirements: Set[PlatformRequirements] = field(default_factory=set)
    frozen: bool = field(default=False, init=False)
    simulations: InitVar[SUPPORTED_SIM_TYPE] = None
    __simulations: Union[SUPPORTED_SIM_TYPE] = field(default_factory=lambda: EntityContainer(), compare=False)

    gather_common_assets_from_task: bool = field(default=False, compare=False)

    def __post_init__(self, simulations):
        super().__post_init__()
        if simulations is not None and not isinstance(simulations, property):
            self.simulations = simulations
        self.__simulations.parent = self

    def __repr__(self):
        return f"<Experiment: {self.uid} - {self.name} / Sim count {len(self.simulations) if self.simulations else 0}>"

    @property
    def suite(self):
        return self.parent

    @suite.setter
    def suite(self, suite):
        self.parent = suite

    def display(self):
        from idmtools.utils.display import display, experiment_table_display
        display(self, experiment_table_display)

    def pre_creation(self) -> None:
        # Gather the assets
        self.gather_assets()

        # to keep experiments clean, let's only do this is we have a special experiment class
        if self.__class__ is not Experiment:
            # Add a tag to keep the Experiment class name
            self.tags["experiment_type"] = f'{self.__class__.__module__}.{self.__class__.__name__}'

        # if it is a template, set task type on experiment
        if isinstance(self.simulations, ParentIterator) and isinstance(self.simulations.items, TemplatedSimulations):
            self.simulations.items.base_task.gather_common_assets()
            self.assets.add_assets(self.simulations.items.base_task.common_assets, fail_on_duplicate=False)
            if "task_type" not in self.tags:
                task_class = self.simulations.items.base_task.__class__
                self.tags["task_type"] = f'{task_class.__module__}.{task_class.__name__}'
        elif self.gather_common_assets_from_task and isinstance(self.__simulations, List):
            task_class = self.simulations[0].task.__class__
            self.tags["task_type"] = f'{task_class.__module__}.{task_class.__name__}'
        elif self.gather_common_assets_from_task:
            for sim in self.simulations:
                assets = sim.task.gather_common_assets()
                if assets is not None:
                    self.assets.add_assets(assets, fail_on_duplicate=False)

        self.tags['idmtools'] = __version__

    @property
    def done(self):
        return all([s.done for s in self.simulations])

    @property
    def succeeded(self):
        return all([s.succeeded for s in self.simulations])

    @property
    def simulations(self):
        return ParentIterator(self.__simulations, parent=self)

    @simulations.setter
    def simulations(self, simulations: Union[SUPPORTED_SIM_TYPE]):
        if isinstance(simulations, (GeneratorType, TemplatedSimulations, EntityContainer)):
            self.__simulations = simulations
        elif isinstance(simulations, (list, set)):
            from idmtools.entities.simulation import Simulation
            self.simulations = EntityContainer()
            for sim in simulations:
                if isinstance(sim, ITask):
                    self.simulations.append(sim.to_simulation())
                elif isinstance(sim, Simulation):
                    self.simulations.append(sim)
                else:
                    raise ValueError("Only list of tasks/simulations can be passed to experiment simulations")
        else:
            raise ValueError("You can only set simulations to an EntityContainer, a Generator, a TemplatedSimulations "
                             "or a List/Set of Simulations")

    @property
    def simulation_count(self):
        return len(self.simulations)

    def refresh_simulations(self):
        from idmtools.core import ItemType
        self.simulations = self.platform.get_children(self.uid, ItemType.EXPERIMENT, force=True)

    def refresh_simulations_status(self):
        self.platform.refresh_status(item=self)

    def pre_getstate(self):
        """
        Return default values for :meth:`~idmtools.interfaces.ientity.pickle_ignore_fields`.
        Call before pickling.
        """
        from idmtools.assets import AssetCollection
        return {"assets": AssetCollection(), "simulations": EntityContainer()}

    def gather_assets(self) -> NoReturn:
        pass

    @classmethod
    def from_task(cls, task, name: str = None, tags: Dict[str, Any] = None, assets: AssetCollection = None,
                  gather_common_assets_from_task: bool = True) -> 'Experiment':
        """
        Creates an Experiment with one Simulation from a task

        Args:
            task: Task to use
            name: Name of experiment
            tags:
            gather_common_assets_from_task: Whether we should attempt to gather assets from the Task object for the
                experiment. With large amounts of tasks, this can be expensive as we loop through all
        Returns:

        """
        if tags is None:
            tags = dict()
        e = Experiment(name=name, tags=tags, assets=AssetCollection() if assets is None else assets,
                       gather_common_assets_from_task=gather_common_assets_from_task)
        e.simulations = [task]
        return e

    @classmethod
    def from_template(cls, template: TemplatedSimulations, name: str = None,
                      tags: Dict[str, Any] = None) -> 'Experiment':
        if tags is None:
            tags = dict()
        e = Experiment(name=name, tags=tags)
        e.simulations = template
        return e

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k in ['_Experiment__simulations'] and isinstance(v, (GeneratorType, TemplatedSimulations)):
                v = list(v)
            setattr(result, k, copy.deepcopy(v, memo))
        result._task_log = getLogger(__name__)
        return result


class ExperimentSpecification(ExperimentPluginSpecification):

    @get_description_impl
    def get_description(self) -> str:
        return "Provides access to the Local Platform to IDM Tools"

    @get_model_impl
    def get(self, configuration: dict) -> Experiment:  # noqa: F821
        """
        Experiment is going
        """
        return Experiment(**configuration)

    @get_model_type_impl
    def get_type(self) -> Type[Experiment]:
        return Experiment
