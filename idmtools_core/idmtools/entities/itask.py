import copy
import time
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field, fields
from logging import getLogger, Logger
from typing import Set, NoReturn, Union, Callable, List, TYPE_CHECKING, Dict
from idmtools.assets import AssetCollection
from idmtools.entities.command_line import CommandLine
from idmtools.entities.platform_requirements import PlatformRequirements
from idmtools.utils.hashing import ignore_fields_in_dataclass_on_pickle

logger = getLogger(__name__)
# Tasks can be allocated multiple ways
# They can be used in Experiments as the description of the item to run within a Simulation
# They can also be used in Workflows to run items
# When used in experiments, it is triggered in the steps
# 1. Create Suite(If Suite)
#    a) Pre-Creation hooks

if TYPE_CHECKING:  # pragma: no cover
    from idmtools.entities.iplatform import IPlatform
    from idmtools.entities.simulation import Simulation
    from idmtools.entities.iworkflow_item import IWorkflowItem  # noqa: F401

TTaskParent = Union['Simulation', 'IWorkflowItem']  # noqa: F821
TTaskHook = Callable[[TTaskParent, 'IPlatform'], NoReturn]


@dataclass
class ITask(metaclass=ABCMeta):
    #: The Command to run
    command: Union[str, CommandLine] = field(default=None, metadata={"md": True})
    #: List of requirements needed by the task to run on an execution platform. This is stuff like Windows, Linux, GPU
    #  etc
    platform_requirements: Set[PlatformRequirements] = field(default_factory=set)

    #: We provide hooks as list to allow more user scripting extensibility
    __pre_creation_hooks: List[TTaskHook] = field(default_factory=list)
    __post_creation_hooks: List[TTaskHook] = field(default_factory=list)
    # This is optional experiment assets
    # That means that users can explicitly define experiment level assets when using a Experiment builders
    #: Common(Experiment-level) assets
    common_assets: AssetCollection = field(default_factory=AssetCollection)
    #: Transient(Simulation-level) assets
    transient_assets: AssetCollection = field(default_factory=AssetCollection)

    # log to add to items to track provisioning of task
    _task_log: Logger = field(default_factory=lambda: getLogger(__name__), compare=False, metadata=dict(pickle_ignore=True))

    def __post_init__(self):
        self._task_log = getLogger(f'{self.__class__.__name__ }_{time.time()}')

        self.__pre_creation_hooks = []
        self.__post_creation_hooks = []

    @property
    def command(self):
        return self._command

    @command.setter
    def command(self, value: Union[str, CommandLine]):
        if isinstance(value, property):
            self._command = None
        elif isinstance(value, str):
            self._command = CommandLine.from_string(value)
        else:
            self._command = value

    @property
    def metadata_fields(self):
        """
        Collect all metadata fields

        Returns: set of metadata filed names
        """
        return set(f.name for f in fields(self) if "md" in f.metadata and f.metadata["md"])

    def add_pre_creation_hook(self, hook: TTaskHook):
        """
        Called before a simulation is created on a platform. Each hook receives either a Simulation or WorkflowTask

        Args:
            hook: Function to call on event

        Returns:
            None
        """
        self.__pre_creation_hooks.append(hook)

    def add_post_creation_hook(self, hook: TTaskHook):
        """
        Called after a simulation has been created on a platform. Each hook receives either a Simulation or WorkflowTask

        Args:
            hook: Function to call on event

        Returns:

        """
        self.__post_creation_hooks.append(hook)

    def add_platform_requirement(self, requirement: Union[PlatformRequirements, str]) -> NoReturn:
        """
        Adds a platform requirements to a task
        Args:
            requirement: Requirement to add task

        Returns:
            None
        """
        if isinstance(requirement, str):
            requirement = PlatformRequirements[requirement.lower()]
        self.platform_requirements.add(requirement)

    def pre_creation(self, parent: Union['Simulation', 'IWorkflowItem'], platform: 'IPlatform'):  # noqa: F821
        """
        Optional Hook called at the time of creation of task. Can be used to setup simulation and experiment level hooks
        Args:
            parent: Parent of Item
            platform: Platform executing the task. Useful for querying platform before execution

        Returns:

        """

        if self.command is None:
            logger.error('Command is not defined')
            raise ValueError("Command is required for on task when preparing an experiment")
        if platform.is_windows_platform():
            self.command.is_windows = True
        [hook(parent, platform) for hook in self.__pre_creation_hooks]

    def post_creation(self, parent: Union['Simulation', 'IWorkflowItem'], platform: 'IPlatform'):  # noqa: F821
        """
        Optional Hook called at the  after creation task. Can be used to setup simulation and experiment level hooks
        Args:
            parent: Parent of Item
            platform: Platform executing the task. Useful for querying platform before execution

        Returns:

        """
        [hook(parent, platform) for hook in self.__post_creation_hooks]

    @abstractmethod
    def gather_common_assets(self) -> AssetCollection:
        """
        Function called at runtime to gather all assets in the collection.
        """
        pass

    @abstractmethod
    def gather_transient_assets(self) -> AssetCollection:
        """
        Function called at runtime to gather all assets in the collection
        """
        pass

    def gather_all_assets(self) -> AssetCollection:
        """
        Collect all common and transient assets

        Returns: new AssetCollection
        """
        return self.gather_common_assets() + self.gather_transient_assets()

    def copy_simulation(self, base_simulation: 'Simulation') -> 'Simulation':
        """
        Called when copying a simulation for batching. Override you your task has specific concerns when copying
         simulations.
        """
        new_simulation = copy.deepcopy(base_simulation)
        return new_simulation

    def reload_from_simulation(self, simulation: 'Simulation'):
        """
        Optional hook that is called when loading simulations from a platform
        """
        raise NotImplementedError("Reloading task from a simulation is not supported")

    def to_simulation(self):
        """
        Convert task to simulation

        Returns: new simulation
        """
        from idmtools.entities.simulation import Simulation
        s = Simulation()
        s.task = self
        return s

    def __repr__(self):
        return f"<{self.__class__.__name__}"

    def pre_getstate(self):
        """
        Return default values for :meth:`~idmtools.interfaces.ientity.pickle_ignore_fields`.
        Call before pickling.

        Returns: dict
        """
        return {"_task_log": None}

    def post_setstate(self):
        self._task_log = getLogger(__name__)

    @property
    def pickle_ignore_fields(self):
        return set(f.name for f in fields(self) if "pickle_ignore" in f.metadata and f.metadata["pickle_ignore"])

    def __getstate__(self):
        """
        Ignore the fields in pickle_ignore_fields during pickling.

        Returns: fields set after removing ignored fields
        """
        return ignore_fields_in_dataclass_on_pickle(self)

    def __setstate__(self, state):
        """
        Add ignored fields back since they don't exist in the pickle
        """
        self.__dict__.update(state)

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k not in ['_task_log']:
                setattr(result, k, copy.deepcopy(v, memo))
        result._task_log = getLogger(__name__)
        return result

    def to_dict(self) -> Dict:
        """
        Select metadata fields and make a new dict

        Returns: dict
        """
        from idmtools_platform_comps.comps_platform import COMPSPlatform
        from idmtools.core.context import get_current_platform

        result = dict()
        metadata_fields = self.metadata_fields
        platform = get_current_platform()
        for f in fields(self):
            if not f.name.startswith("_") and f.name not in ['parent']:
                if isinstance(platform, COMPSPlatform):
                    if f.name in metadata_fields:
                        result[f.name] = getattr(self, f.name)
                    else:
                        result[f.name] = f.default
                else:
                    result[f.name] = getattr(self, f.name)
        return result
