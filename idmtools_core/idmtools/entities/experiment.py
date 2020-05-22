import copy
import uuid
from dataclasses import dataclass, field, InitVar
from logging import getLogger
from types import GeneratorType
from typing import NoReturn, Set, Union, Iterator, Type, Dict, Any, List

from idmtools.assets import AssetCollection
from idmtools.builders import SimulationBuilder
from idmtools.core import ItemType, NoPlatformException, EntityStatus
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

    # whether we should gather assets from the first task. This should be autodected based on simulations
    gather_common_assets_from_task: bool = field(default=None, compare=False)

    # control whether we should replace the task with a proxy after creation to conser
    __replace_task_with_proxy: bool = field(default=True, init=False, compare=False)

    def __post_init__(self, simulations):
        super().__post_init__()
        if simulations is not None and not isinstance(simulations, property):
            self.simulations = simulations

        if self.gather_common_assets_from_task is None:
            self.gather_common_assets_from_task = isinstance(self.simulations.items, EntityContainer)
        self.__simulations.parent = self

        # set initial status. Experiment may be new or reloaded.
        if any([s.status == EntityStatus.CREATED for s in self.simulations]):
            self.status = EntityStatus.CREATED
        elif any([s.status == EntityStatus.RUNNING for s in self.simulations]):
            self.status = EntityStatus.RUNNING
        elif all([s.status == EntityStatus.SUCCEEDED for s in self.simulations]):
            self.status = EntityStatus.SUCCEEDED
        elif any([s.status == EntityStatus.FAILED for s in self.simulations]):
            self.status = EntityStatus.FAILED

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
            self.simulations.items.base_task.gather_common_assets()
            self.assets.add_assets(self.simulations.items.base_task.common_assets, fail_on_duplicate=False)
            if "task_type" not in self.tags:
                task_class = self.simulations.items.base_task.__class__
                self.tags["task_type"] = f'{task_class.__module__}.{task_class.__name__}'
        elif self.gather_common_assets_from_task and isinstance(self.__simulations, List):
            task_class = self.simulations[0].task.__class__
            self.tags["task_type"] = f'{task_class.__module__}.{task_class.__name__}'
            for sim in self.simulations:
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
    def simulations(self):
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

    def run(self, wait_until_done: bool = False, platform: 'idmtools.entities.iplatform.IPlatform' = None,  # noqa: F821
            **run_opts) -> NoReturn:
        """
        Runs an experiment on a platform

        Args:
            wait_until_done: Whether we should wait on experiment to finish running as well. Defaults to False
            platform: Platform object to use. If not specified, we first check object for platform object then the current context
            **run_opts: Options to pass to the platform

        Returns:
            None
        """
        p = self.__check_for_platform_from_context(platform)
        p.run_items(self, **run_opts)
        if wait_until_done:
            self.wait()

    def __check_for_platform_from_context(self, platform) -> 'idmtools.entities.iplatform.IPlatform':  # noqa: F821
        """
        Try to determine platform of current object from self or current platform

        Args:
            platform: Passed in platform object

        Raises:
            NoPlatformException: when no platform is on current context
        Returns:
            Platform object
        """
        if self.platform is None:
            # check context for current platform
            if platform is None:
                from idmtools.core.platform_factory import current_platform
                if current_platform is None:
                    raise NoPlatformException("No Platform defined on object, in current context, or passed to run")
                platform = current_platform
            self.platform = platform
        return self.platform

    def wait(self, timeout: int = None, refresh_interval=None,
             platform: 'idmtools.entities.iplatform.IPlatform' = None):  # noqa: F821
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
        p = self.__check_for_platform_from_context(platform)
        p.wait_till_done_progress(self, **opts)

    def add_new_simulations(self, simulations: TemplatedSimulations):
        """
        Add simulations to a pre-existing experiment containing simulations that may have already been run.

        Args:
            simulations: TemplatedSimulations object containing builders/sims to add to pre-existing experiment

        Returns:
            Nothing
        """
        if not isinstance(simulations, TemplatedSimulations):
            raise TypeError('Adding new simulations to existing experiments requires a TemplatedSimulations object '
                            'containing the new simulation(s) and/or simulation builder(s).')

        # merge existing self.simulations object builders and single simulations into new simulations object
        if isinstance(self.simulations.items, TemplatedSimulations):
            for builder in self.simulations.items.builders:
                simulations.add_builder(builder=builder)
            existing_additional_simulations = self.simulations.items.__extra_simulations
        else:
            existing_additional_simulations = self.simulations

        for simulation in existing_additional_simulations:
            simulations.add_simulation(simulation=simulation)

        # set experiment simulations to merged object and update experiment status
        self.simulations = simulations
        self.status = EntityStatus.CREATED


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
