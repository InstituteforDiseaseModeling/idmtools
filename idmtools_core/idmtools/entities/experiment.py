import copy
import uuid
from dataclasses import dataclass, field, InitVar, fields
from logging import getLogger, DEBUG
from types import GeneratorType
from typing import NoReturn, Set, Union, Iterator, Type, Dict, Any, List, TYPE_CHECKING, Generator

from tqdm import tqdm

from idmtools.assets import AssetCollection, Asset
from idmtools.builders import SimulationBuilder
from idmtools.core import ItemType, EntityStatus
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
from idmtools.utils.entities import get_default_tags

if TYPE_CHECKING:
    from idmtools.entities.iplatform import IPlatform
    from idmtools.entities.simulation import Simulation

logger = getLogger(__name__)
SUPPORTED_SIM_TYPE = Union[
    EntityContainer,
    Generator['Simulation', None, None],
    TemplatedSimulations,
    Iterator['Simulation']
]


@dataclass(repr=False)
class Experiment(IAssetsEnabled, INamedEntity):
    """
    Class that represents a generic experiment.
    This class needs to be implemented for each model type with specifics.

    Args:
        name: The experiment name.
        assets: The asset collection for assets global to this experiment.
    """
    #: Suite ID
    suite_id: uuid = field(default=None)
    #: Item Item(always an experiment)
    item_type: ItemType = field(default=ItemType.EXPERIMENT, compare=False, init=False)
    #: Task Type(defaults to command)
    task_type: str = field(default='idmtools.entities.command_task.CommandTask')
    #: List of Requirements for the task that a platform must meet to be able to run
    platform_requirements: Set[PlatformRequirements] = field(default_factory=set)
    #: Is the Experiment Frozen
    frozen: bool = field(default=False, init=False)
    #: Simulation in this experiment
    simulations: InitVar[SUPPORTED_SIM_TYPE] = None
    #: Internal storage of simulation
    __simulations: Union[SUPPORTED_SIM_TYPE] = field(default_factory=lambda: EntityContainer(), compare=False)

    #: Determines if we should gather assets from a the first task. Only use when not using TemplatedSimulations
    gather_common_assets_from_task: bool = field(default=None, compare=False)

    #: Enable replacing the task with a proxy to reduce the memory footprint. Useful in provisioning large sets of
    # simulations
    __replace_task_with_proxy: bool = field(default=True, init=False, compare=False)

    def __post_init__(self, simulations):
        super().__post_init__()
        if simulations is not None and not isinstance(simulations, property):
            self.simulations = simulations

        if self.gather_common_assets_from_task is None:
            self.gather_common_assets_from_task = isinstance(self.simulations.items, EntityContainer)
        self.__simulations.parent = self

    def __repr__(self):
        return f"<Experiment: {self.uid} - {self.name} / Sim count {len(self.simulations) if self.simulations else 0}>"

    @property
    def suite(self):
        return self.parent

    @suite.setter
    def suite(self, suite):
        ids = [exp.uid for exp in suite.experiments]
        if self.uid not in ids:
            suite.experiments.append(self)
            self.parent = suite

    def display(self):
        from idmtools.utils.display import display, experiment_table_display
        display(self, experiment_table_display)

    def pre_creation(self) -> None:
        """
        Experiment pre_creation callback

        Returns:

        """
        # Gather the assets
        self.gather_assets()

        # to keep experiments clean, let's only do this is we have a special experiment class
        if self.__class__ is not Experiment:
            # Add a tag to keep the Experiment class name
            self.tags["experiment_type"] = f'{self.__class__.__module__}.{self.__class__.__name__}'

        # if it is a template, set task type on experiment
        if isinstance(self.simulations, ParentIterator) and isinstance(self.simulations.items, TemplatedSimulations):
            if logger.isEnabledFor(DEBUG):
                logger.debug("Using Base task from template for experiment level assets")
            self.simulations.items.base_task.gather_common_assets()
            self.assets.add_assets(self.simulations.items.base_task.common_assets, fail_on_duplicate=False)
            if "task_type" not in self.tags:
                task_class = self.simulations.items.base_task.__class__
                self.tags["task_type"] = f'{task_class.__module__}.{task_class.__name__}'
        elif self.gather_common_assets_from_task and isinstance(self.__simulations, List):
            if logger.isEnabledFor(DEBUG):
                logger.debug("Using first task for task type")
                logger.debug("Using all tasks to gather assts")
            task_class = self.__simulations[0].task.__class__
            self.tags["task_type"] = f'{task_class.__module__}.{task_class.__name__}'
            pbar = tqdm(self.__simulations, desc="Discovering experiment assets from tasks")
            for sim in pbar:
                # don't gather assets from simulations that have been provisioned
                if sim.status is None:
                    assets = sim.task.gather_common_assets()
                    if assets is not None:
                        self.assets.add_assets(assets, fail_on_duplicate=False)

        self.tags.update(get_default_tags())

    @property
    def done(self):
        """
        Return if an experiment has finished executing

        Returns:
            True if all simulations have ran, False otherwise
        """
        return all([s.done for s in self.simulations])

    @property
    def succeeded(self) -> bool:
        """
        Return if an experiment has succeeded. An experiment is succeeded when all simulations have succeeded

        Returns:
            True if all simulations have succeeded, False otherwise
        """
        return all([s.succeeded for s in self.simulations])

    @property
    def simulations(self) -> Iterator['Simulation']:
        return ParentIterator(self.__simulations, parent=self)

    @simulations.setter
    def simulations(self, simulations: Union[SUPPORTED_SIM_TYPE]):
        """
        Set the simulations object

        Args:
            simulations:

        Returns:

        """
        if isinstance(simulations, (GeneratorType, TemplatedSimulations, EntityContainer)):
            self.gather_common_assets_from_task = isinstance(simulations, (GeneratorType, EntityContainer))
            self.__simulations = simulations
        elif isinstance(simulations, (list, set)):
            from idmtools.entities.simulation import Simulation
            self.gather_common_assets_from_task = True
            self.__simulations = EntityContainer()
            for sim in simulations:
                if isinstance(sim, ITask):
                    self.__simulations.append(sim.to_simulation())
                elif isinstance(sim, Simulation):
                    self.__simulations.append(sim)
                else:
                    raise ValueError("Only list of tasks/simulations can be passed to experiment simulations")
        else:
            raise ValueError("You can only set simulations to an EntityContainer, a Generator, a TemplatedSimulations "
                             "or a List/Set of Simulations")

    @property
    def simulation_count(self) -> int:
        """
        Return the total simulations
        Returns:

        """
        return len(self.simulations)

    def refresh_simulations(self) -> NoReturn:
        """
        Refresh the simulations from the platform

        Returns:

        """
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
            assets: Asset collection to use for common tasks. Defaults to gather assets from task
            name: Name of experiment
            tags:
            gather_common_assets_from_task: Whether we should attempt to gather assets from the Task object for the
                experiment. With large amounts of tasks, this can be expensive as we loop through all
        Returns:

        """
        if tags is None:
            tags = dict()
        if name is None:
            name = task.__class__.__name__
        e = Experiment(name=name, tags=tags, assets=AssetCollection() if assets is None else assets,
                       gather_common_assets_from_task=gather_common_assets_from_task)
        e.simulations = [task]
        return e

    @classmethod
    def from_builder(cls, builders: Union[SimulationBuilder, List[SimulationBuilder]], base_task: ITask,
                     name: str = None,
                     assets: AssetCollection = None, tags: Dict[str, Any] = None) -> 'Experiment':
        """
        Creates an experiment from a SimulationBuilder object(or list of builders

        Args:
            builders: List of builder to create experiment from
            base_task: Base task to use as template
            name: Experiment name
            assets: Experiment level assets
            tags: Experiment tags

        Returns:
            Experiment object from the builders
        """
        ts = TemplatedSimulations(base_task=base_task)
        if not isinstance(builders, list):
            builders = [builders]
        for builder in builders:
            ts.add_builder(builder)
        if name is None:
            name = base_task.__class__.__name__
            if len(builders) == 1:
                name += " " + builders[0].__class__.__name__
        return cls.from_template(ts, name=name, tags=tags, assets=assets)

    @classmethod
    def from_template(cls, template: TemplatedSimulations, name: str = None, assets: AssetCollection = None,
                      tags: Dict[str, Any] = None) -> 'Experiment':
        """
        Creates an Experiment from a TemplatedSimulation object

        Args:
            template: TemplatedSimulation object
            name: Experiment name
            assets: Experiment level assets
            tags: Tags

        Returns:
            Experiment object from the TemplatedSimulation object
        """
        if tags is None:
            tags = dict()
        if name is None:
            name = template.base_task.__class__.__name__
        e = Experiment(name=name, tags=tags, assets=AssetCollection() if assets is None else assets)
        e.simulations = template
        return e

    def __deepcopy__(self, memo):
        """
        Deep copy for experiments. It converts generators and templates to realized lists to allow copying

        Args:
            memo: The memo object used for copying

        Returns:
            Copied experiment
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k in ['_Experiment__simulations'] and isinstance(v, (GeneratorType, TemplatedSimulations)):
                v = list(v)
            setattr(result, k, copy.deepcopy(v, memo))
        result._task_log = getLogger(__name__)
        return result

    def list_static_assets(self, children: bool = False, platform: 'IPlatform' = None, **kwargs) -> List[Asset]:
        """
        List assets that have been uploaded to a server already

        Args:
            children: When set to true, simulation assets will be loaded as well
            platform: Optional platform to load assets list from
            **kwargs:

        Returns:
            List of assets
        """
        if self.id is None:
            raise ValueError("You can only list static assets on an existing experiment")
        p = super()._check_for_platform_from_context(platform)
        return p._experiments.list_assets(self, children, **kwargs)

    def run(self, wait_until_done: bool = False, platform: 'IPlatform' = None, **run_opts) -> NoReturn:
        """
        Runs an experiment on a platform

        Args:
            wait_until_done: Whether we should wait on experiment to finish running as well. Defaults to False
            platform: Platform object to use. If not specified, we first check object for platform object then the current context
            **run_opts: Options to pass to the platform

        Returns:
            None
        """
        p = super()._check_for_platform_from_context(platform)
        p.run_items(self, **run_opts)
        if wait_until_done:
            self.wait()

    def wait(self, timeout: int = None, refresh_interval=None, platform: 'IPlatform' = None):
        """
        Wait on an experiment to finish running

        Args:
            timeout: Timeout to wait
            refresh_interval: How often to refresh object
            platform: Platform. If not specified, we try to determine this from context

        Returns:

        """
        if self.status not in [EntityStatus.CREATED, EntityStatus.RUNNING]:
            raise ValueError("The experiment cannot be waited for if it is not in Running/Created state")
        opts = dict()
        if timeout:
            opts['timeout'] = timeout
        if refresh_interval:
            opts['refresh_interval'] = refresh_interval
        p = super()._check_for_platform_from_context(platform)
        p.wait_till_done_progress(self, **opts)

    def to_dict(self):
        result = dict()
        for f in fields(self):
            if not f.name.startswith("_") and f.name not in ['parent']:
                result[f.name] = getattr(self, f.name)

        result['simulations'] = [s.id for s in self.simulations]
        result['_uid'] = self.uid
        return result

    # Define this here for better completion in IDEs for end users
    @classmethod
    def from_id(cls, item_id: Union[str, uuid.UUID], platform: 'IPlatform' = None, **kwargs) -> 'Experiment':
        return super().from_id(item_id, platform, **kwargs)


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
