"""
Our Experiment class definition.

Experiments can be thought of as a metadata object analogous to a folder on a filesystem. An experiment is a container that
contains one or more simulations. Before creations, *experiment.simulations* can be either a list of a TemplatedSimulations.
TemplatedSimulations are useful for building large numbers of similar simulations such as sweeps.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import copy
import warnings
from dataclasses import dataclass, field, InitVar, fields
from logging import getLogger, DEBUG
from types import GeneratorType
from typing import NoReturn, Set, Union, Iterator, Type, Dict, Any, List, TYPE_CHECKING, Generator
from idmtools import IdmConfigParser
from idmtools.assets import AssetCollection, Asset
from idmtools.builders import SimulationBuilder
from idmtools.core import ItemType, EntityStatus
from idmtools.core.interfaces.entity_container import EntityContainer
from idmtools.core.interfaces.iassets_enabled import IAssetsEnabled
from idmtools.core.interfaces.iitem import IItem
from idmtools.core.interfaces.inamed_entity import INamedEntity
from idmtools.core.interfaces.irunnable_entity import IRunnableEntity
from idmtools.core.logging import SUCCESS, NOTICE
from idmtools.entities.itask import ITask
from idmtools.core.interfaces.ientity import IEntity
from idmtools.entities.platform_requirements import PlatformRequirements
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools.registry.experiment_specification import ExperimentPluginSpecification, get_model_impl, \
    get_model_type_impl
from idmtools.registry.plugin_specification import get_description_impl
from idmtools.utils.caller import get_caller
from idmtools.utils.collections import ExperimentParentIterator
from idmtools.utils.entities import get_default_tags

if TYPE_CHECKING:  # pragma: no cover
    from idmtools.entities.iplatform import IPlatform
    from idmtools.entities.simulation import Simulation  # noqa: F401

logger = getLogger(__name__)
user_logger = getLogger('user')
SUPPORTED_SIM_TYPE = Union[
    EntityContainer,
    Generator['Simulation', None, None],
    TemplatedSimulations,
    Iterator['Simulation']
]


@dataclass(repr=False)
class Experiment(IAssetsEnabled, INamedEntity, IRunnableEntity):
    """
    Class that represents a generic experiment.

    This class needs to be implemented for each model type with specifics.

    Args:
        name: The experiment name.
        assets: The asset collection for assets global to this experiment.
    """
    #: Suite ID
    suite_id: str = field(default=None)
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

    #: Determines if we should gather assets from the first task. Only use when not using TemplatedSimulations
    gather_common_assets_from_task: bool = field(default=None, compare=False)

    #: Determines if we should gather assets from the first task. Only use when not using TemplatedSimulations
    disable_default_pre_create: bool = field(default=False, compare=False)

    #: Enable replacing the task with a proxy to reduce the memory footprint. Useful in provisioning large sets of
    # simulations
    __replace_task_with_proxy: bool = field(default=True, init=False, compare=False)

    def __post_init__(self, simulations):
        """
        Initialize Experiment.

        Args:
            simulations: Simulations to initialize with

        Returns:
            None
        """
        super().__post_init__()
        if simulations is not None and not isinstance(simulations, property):
            self.simulations = simulations

        if self.gather_common_assets_from_task is None:
            self.gather_common_assets_from_task = isinstance(self.simulations.items, EntityContainer)
        self.__simulations.parent = self

    def post_creation(self, platform: 'IPlatform') -> None:
        """
        Post creation of experiments.

        Args:
            platform: Platform the experiment was created on

        Returns:
            None
        """
        IItem.post_creation(self, platform)

    @property
    def status(self):
        """
        Get status of experiment. Experiment status is based in simulations.

        The first rule to be true is used. The rules are:
        * If simulations is a TemplatedSimulations we assume status is None if _platform_object is not set.
        * If simulations is a TemplatedSimulations we assume status is CREATED if _platform_object is set.
        * If simulations length is 0 or all simulations have a status of None, experiment status is none
        * If any simulation has a running status, experiment is considered running.
        * If any simulation has a created status and any other simulation has a FAILED or SUCCEEDED status, experiment is considered running.
        * If any simulation has a None status and any other simulation has a FAILED or SUCCEEDED status, experiment is considered Created.
        * If any simulation has a status of failed, experiment is considered failed.
        * If any simulation has a status of SUCCEEDED, experiment is considered SUCCEEDED.
        * If any simulation has a status of CREATED, experiment is considered CREATED.


        Returns:
            Status
        """
        # still creating sims since we have a template. When adding new simulations, we will pre-create sim objects unless
        # the item is new
        if isinstance(self.simulations.items, TemplatedSimulations):
            status = EntityStatus.CREATED if self._platform_object else None
            return status

        sim_statuses = set([s.status for s in self.simulations.items])
        any_succeeded_failed = any([s in [EntityStatus.FAILED, EntityStatus.SUCCEEDED] for s in sim_statuses])
        if len(self.simulations.items) == 0 or all([s is None for s in sim_statuses]):
            status = None  # this will trigger experiment creation on a platform
        elif any([s == EntityStatus.RUNNING for s in sim_statuses]):
            status = EntityStatus.RUNNING
        elif any([s == EntityStatus.CREATED for s in sim_statuses]) and any_succeeded_failed:
            status = EntityStatus.RUNNING
        elif any([s is None for s in sim_statuses]) and any_succeeded_failed:
            status = EntityStatus.CREATED
        elif any([s == EntityStatus.FAILED for s in sim_statuses]):
            status = EntityStatus.FAILED
        elif all([s == EntityStatus.SUCCEEDED for s in sim_statuses]):
            status = EntityStatus.SUCCEEDED
        else:
            status = EntityStatus.CREATED
        return status

    @status.setter
    def status(self, value):
        """
        Set status of experiment. Experiments status is an aggregate of its children so you cannot set status.

        Args:
            value: Value to set

        Returns:
            None

        Notes:
            TODO: Deprecate this
        """
        # this method is needed because dataclasses will always try to set each field, even if not allowed to in
        # the case of Experiment.

        caller = get_caller()
        if caller not in ['__init__']:
            logger.warning('Experiment status cannot be directly altered. Status unchanged.')

    def __repr__(self):
        """Experiment as string."""
        return f"<Experiment: {self.uid} - {self.name} / Sim count {len(self.simulations) if self.simulations else 0}>"

    @property
    def suite(self):
        """
        Suite the experiment belongs to.

        Returns:
            Suite
        """
        return self.parent

    @suite.setter
    def suite(self, suite):
        """
        Set suite of the experiment.

        Args:
            suite: Suite to set

        Returns:
            None
        """
        self.parent = suite

    @IEntity.parent.setter
    def parent(self, parent: 'IEntity'):
        """
        Sets the parent object for Entity.

        Args:
            parent: Parent object

        Returns:
            None
        """
        if parent:
            if parent.experiments is None:
                parent.experiments = [self]
            else:
                parent.experiments.append(self)
        IEntity.parent.__set__(self, parent)

    def display(self):
        """
        Display the experiment.

        Returns:
            None
        """
        from idmtools.utils.display import display, experiment_table_display
        display(self, experiment_table_display)

    def pre_creation(self, platform: 'IPlatform', gather_assets=True) -> None:
        """
        Experiment pre_creation callback.

        Args:
            platform: Platform experiment is being created on
            gather_assets: Determines if an experiment will try to gather the common assets or defer. It most cases, you want this enabled but when modifying existing experiments you may want to disable if there are new assets and the platform has performance hits to determine those assets

        Returns:
            None

        Raises:
            ValueError - If simulations length is 0
        """
        # Gather the assets
        IItem.pre_creation(self, platform)
        if not self.disable_default_pre_create:
            self.gather_assets()

            # to keep experiments clean, let's only do this is we have a special experiment class
            if self.__class__ is not Experiment:
                # Add a tag to keep the Experiment class name
                self.tags["experiment_type"] = f'{self.__class__.__module__}.{self.__class__.__name__}'

            # if it is a template, set task type on experiment
            if gather_assets:
                if isinstance(self.simulations.items, TemplatedSimulations):
                    if len(self.simulations.items) == 0:
                        raise ValueError("You cannot run an empty experiment")
                    if logger.isEnabledFor(DEBUG):
                        logger.debug("Using Base task from template for experiment level assets")
                    self.simulations.items.base_task.gather_common_assets()
                    self.assets.add_assets(self.simulations.items.base_task.common_assets, fail_on_duplicate=False)
                    for sim in self.simulations.items.extra_simulations():
                        self.assets.add_assets(sim.task.gather_common_assets(), fail_on_duplicate=False)
                    if "task_type" not in self.tags:
                        task_class = self.simulations.items.base_task.__class__
                        self.tags["task_type"] = f'{task_class.__module__}.{task_class.__name__}'
                elif self.gather_common_assets_from_task and isinstance(self.simulations.items, List):
                    if len(self.simulations.items) == 0:
                        raise ValueError("You cannot run an empty experiment")
                    if logger.isEnabledFor(DEBUG):
                        logger.debug("Using all tasks to gather assets")
                    task_class = self.__simulations[0].task.__class__
                    self.tags["task_type"] = f'{task_class.__module__}.{task_class.__name__}'
                    pbar = self.__simulations
                    if not IdmConfigParser.is_progress_bar_disabled():
                        from tqdm import tqdm
                        pbar = tqdm(self.__simulations, desc="Discovering experiment assets from tasks",
                                    unit="simulation")
                    for sim in pbar:
                        # don't gather assets from simulations that have been provisioned
                        if sim.status is None:
                            assets = sim.task.gather_common_assets()
                            if assets is not None:
                                self.assets.add_assets(assets, fail_on_duplicate=True, fail_on_deep_comparison=True)
                elif isinstance(self.simulations.items, List) and len(self.simulations.items) == 0:
                    raise ValueError("You cannot run an empty experiment")

            self.tags.update(get_default_tags())

    @property
    def done(self):
        """
        Return if an experiment has finished executing.

        Returns:
            True if all simulations have ran, False otherwise
        """
        return all([s.done for s in self.simulations])

    @property
    def succeeded(self) -> bool:
        """
        Return if an experiment has succeeded. An experiment is succeeded when all simulations have succeeded.

        Returns:
            True if all simulations have succeeded, False otherwise
        """
        return all([s.succeeded for s in self.simulations])

    @property
    def any_failed(self) -> bool:
        """
        Return if an experiment has any simulation in failed state.

        Returns:
            True if all simulations have succeeded, False otherwise
        """
        return any([s.failed for s in self.simulations])

    @property
    def simulations(self) -> ExperimentParentIterator:
        """
        Returns the Simulations.

        Returns:
            Simulations
        """
        return ExperimentParentIterator(self.__simulations, parent=self)

    @simulations.setter
    def simulations(self, simulations: Union[SUPPORTED_SIM_TYPE]):
        """
        Set the simulations object.

        Args:
            simulations:

        Returns:
            None

        Raises:
            ValueError - If simulations is a list has items that are not simulations or tasks
                         If simulations is not a list, set, TemplatedSimulations or EntityContainer
        """
        if isinstance(simulations, (GeneratorType, TemplatedSimulations, EntityContainer)):
            self.gather_common_assets_from_task = isinstance(simulations, (GeneratorType, EntityContainer))
            self.__simulations = simulations
        elif isinstance(simulations, (list, set)):
            from idmtools.entities.simulation import Simulation  # noqa: F811
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
        Return the total simulations.

        Returns:
            Length of simulations
        """
        return len(self.simulations)

    def refresh_simulations(self) -> NoReturn:
        """
        Refresh the simulations from the platform.

        Returns:
            None
        """
        from idmtools.core import ItemType
        self.simulations = self.platform.get_children(self.uid, ItemType.EXPERIMENT, force=True)

    def refresh_simulations_status(self):
        """
        Refresh the simulation status.

        Returns:
            None
        """
        self.platform.refresh_status(item=self)

    def pre_getstate(self):
        """
        Return default values for :meth:`~idmtools.interfaces.ientity.pickle_ignore_fields`.

        Call before pickling.
        """
        from idmtools.assets import AssetCollection
        return {"assets": AssetCollection(), "simulations": EntityContainer()}

    def gather_assets(self) -> AssetCollection():
        """
        Gather all our assets for our experiment.

        Returns:
            Assets
        """
        return self.assets

    @classmethod
    def from_task(cls, task, name: str = None, tags: Dict[str, Any] = None, assets: AssetCollection = None,
                  gather_common_assets_from_task: bool = True) -> 'Experiment':
        """
        Creates an Experiment with one Simulation from a task.

        Args:
            task: Task to use
            assets: Asset collection to use for common tasks. Defaults to gather assets from task
            name: Name of experiment
            tags: Tags for the items
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
        Creates an experiment from a SimulationBuilder object(or list of builders.

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
        Creates an Experiment from a TemplatedSimulation object.

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
        Deep copy for experiments. It converts generators and templates to realized lists to allow copying.

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
        List assets that have been uploaded to a server already.

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

    def run(self, wait_until_done: bool = False, platform: 'IPlatform' = None, regather_common_assets: bool = None,
            wait_on_done_progress: bool = True, **run_opts) -> NoReturn:
        """
        Runs an experiment on a platform.

        Args:
            wait_until_done: Whether we should wait on experiment to finish running as well. Defaults to False
            platform: Platform object to use. If not specified, we first check object for platform object then the current context
            regather_common_assets: Triggers gathering of assets for *existing* experiments. If not provided, we use the platforms default behaviour. See platform details for performance implications of this. For most platforms, it should be ok but for others, it could decrease performance when assets are not changing.
              It is important to note that when using this feature, ensure the previous simulations have finished provisioning. Failure to do so can lead to unexpected behaviour
            wait_on_done_progress: Should experiment status be shown when waiting
            **run_opts: Options to pass to the platform

        Returns:
            None
        """
        p = super()._check_for_platform_from_context(platform)
        if 'wait_on_done' in run_opts:
            warnings.warn("wait_on_done will be deprecated soon. Please use wait_until_done instead.", DeprecationWarning, 2)
            user_logger.warning("wait_on_done will be deprecated soon. Please use wait_until_done instead.")
        if regather_common_assets is None:
            regather_common_assets = p.is_regather_assets_on_modify()
        if regather_common_assets and not self.assets.is_editable():
            message = "To modify an experiment's asset collection, you must make a copy of it first. For example\nexperiment.assets = experiment.assets.copy()"
            user_logger.error(message)  # Show it bold red to user
            raise ValueError(message)
        if not self.assets.is_editable() and isinstance(self.simulations.items,
                                                        TemplatedSimulations) and not regather_common_assets:
            user_logger.warning(
                "You are modifying and existing experiment by using a template without gathering common assets. Ensure your Template configuration is the same as existing experiments or enable gathering of new common assets through regather_common_assets.")
        run_opts['regather_common_assets'] = regather_common_assets
        p.run_items(self, **run_opts)
        if wait_until_done or run_opts.get('wait_on_done', False):
            self.wait(wait_on_done_progress=wait_on_done_progress)

    def to_dict(self):
        """
        Convert experiment to dictionary.

        Returns:
            Dictionary of experiment.
        """
        result = dict()
        for f in fields(self):
            if not f.name.startswith("_") and f.name not in ['parent']:
                result[f.name] = getattr(self, f.name)

        result['_uid'] = self.uid
        return result

    # Define this here for better completion in IDEs for end users
    @classmethod
    def from_id(cls, item_id: str, platform: 'IPlatform' = None, copy_assets: bool = False,
                **kwargs) -> 'Experiment':
        """
        Helper function to provide better intellisense to end users.

        Args:
            item_id: Item id to load
            platform: Optional platform. Fallbacks to context
            copy_assets: Allow copying assets on load. Makes modifying experiments easier when new assets are involved.
            **kwargs: Optional arguments to be passed on to the platform

        Returns:
            Experiment loaded with ID
        """
        result = super().from_id(item_id, platform, **kwargs)
        if copy_assets:
            result.assets = result.assets.copy()
        return result

    def print(self, verbose: bool = False):
        """
        Print summary of experiment.

        Args:
            verbose: Verbose printing

        Returns:
            None
        """
        user_logger.info(f"Experiment <{self.id}>")
        user_logger.info(f"Total Simulations: {self.simulation_count}")
        user_logger.info(f"Tags: {self.tags}")
        user_logger.info(f"Platform: {self.platform.__class__.__name__}")
        # determine status
        if self.status:
            # if succeeded print that
            if self.succeeded:
                user_logger.log(SUCCESS, "Succeeded")
            elif not self.done:
                user_logger.log(NOTICE, "RUNNING")
            else:
                user_logger.critical("Experiment failed. Please check output")

        if verbose:
            user_logger.info(f"Simulation Type: {type(self.__simulations)}")
            user_logger.info(f"Assets: {self.assets}")


class ExperimentSpecification(ExperimentPluginSpecification):
    """
    ExperimentSpecification is the spec for Experiment plugins.
    """

    @get_description_impl
    def get_description(self) -> str:
        """
        Description of our plugin.

        Returns:
            Description
        """
        return "Provides access to the Local Platform to IDM Tools"

    @get_model_impl
    def get(self, configuration: dict) -> Experiment:  # noqa: F821
        """
        Get experiment with configuration.
        """
        return Experiment(**configuration)

    @get_model_type_impl
    def get_type(self) -> Type[Experiment]:
        """
        Return the experiment type.

        Returns:
            Experiment type.
        """
        return Experiment
