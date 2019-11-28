import copy
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from logging import getLogger
from typing import Set, NoReturn, Union, Callable, List, Optional
from idmtools.assets import AssetCollection
from idmtools.core.interfaces.iassets_enabled import IAssetsEnabled
from idmtools.entities.command_line import CommandLine
from idmtools.entities.platform_requirements import PlatformRequirements


logger = getLogger(__name__)
# Tasks can be allocated multiple ways
# They can be used in Experiments as the description of the item to run within a Simulation
# They can also be used in Workflows to run items
# When used in experiments, it is triggered in the steps
# 1. Create Suite(If Suite)
#    a) Pre-Creation hooks


TTaskParent = Union['Simulation', 'WorkflowItem']
TTaskHook = Callable[[TTaskParent], NoReturn]


@dataclass
class ITask(IAssetsEnabled, metaclass=ABCMeta):
    command: CommandLine = None
    # Informs platform to what is needed to run a task
    platform_requirements: Set[PlatformRequirements] = field(default_factory=lambda: [])

    # We provide hooks as list to allow more user scripting extensibility
    __pre_creation_hooks: List[TTaskHook] = None
    __post_creation_hooks: List[TTaskHook] = None
    # This is optional experiment assets
    # That means that users can explicitly define experiment level assets when using a Experiment builders
    experiment_assets: Optional[AssetCollection] = None

    def __post_init__(self):
        if isinstance(self.command, str):
            self.command = CommandLine(self.command)

        self.__pre_creation_hooks = []
        self.__post_creation_hooks = []

    def add_pre_creation_hook(self, hook: TTaskHook):
        self.__pre_creation_hooks.append(hook)

    def add_post_creation_hook(self, hook: TTaskHook):
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

    def pre_creation(self, parent: Union['Simulation', 'WorkflowItem']):
        """
        Optional Hook called at the time of creation of task. Can be used to setup simulation and experiment level hooks
        Args:
            parent:

        Returns:

        """
        if self.command is None:
            logger.error('Command is not defined')
            raise ValueError("Command is required for on task when preparing an experiment")
        [hook(parent) for hook in self.__pre_creation_hooks]


    def post_creation(self, parent: Union['Simulation', 'WorkflowItem']):
        """
        Optional Hook called at the  after creation task. Can be used to setup simulation and experiment level hooks
        Args:
            parent:

        Returns:

        """
        [hook(parent) for hook in self.__post_creation_hooks]

    @abstractmethod
    def gather_assets(self) -> NoReturn:
        """
        Function called at runtime to gather all assets in the collection
        """
        pass

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
