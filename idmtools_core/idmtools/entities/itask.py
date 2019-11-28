import copy
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Set, NoReturn, Union
from idmtools.core.interfaces.iassets_enabled import IAssetsEnabled
from idmtools.entities.command_line import CommandLine
from idmtools.entities.platform_requirements import PlatformRequirements


@dataclass
class ITask(IAssetsEnabled, metaclass=ABCMeta):
    command: CommandLine = None
    # Informs platform to what is needed to run a task
    platform_requirements: Set[PlatformRequirements] = field(default_factory=lambda: [])

    def __post_init__(self):
        if self.command is None:  # there should be a better way to do this with dataclasses
            raise ValueError("Command is required")
        if isinstance(self.command, str):
            self.command = CommandLine(self.command)

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

    @abstractmethod
    def init(self, simulation):
        """
        Hook called at the time of creation of task. Can be used to setup simulation and experiment level hooks
        Args:
            simulation:

        Returns:

        """
        pass

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

    @staticmethod
    def reload_from_simulation(simulation: 'Simulation') -> 'ITask':
        """
        Optional hook that is called when loading simulations from a platform
        """
        raise NotImplementedError("Reloading task from a simulation is not supported")
