"""
Here we implement the base operations interfaces for all file based platforms.

Copyright 2025, Gates Foundation. All rights reserved.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Type, Union, Any
from idmtools.core import ItemType
from idmtools.core.interfaces.ientity import IEntity
from idmtools.entities.simulation import Simulation


@dataclass
class IOperations(ABC):
    """
    Abstract base class defining platform-specific operations.

    This interface should be implemented by platform FilePlatform or SlurmPlatform
    to handle directory structure, job submission, and file linking.
    """
    platform: 'FilePlatform'  # noqa: F821
    platform_type: Type = field(default=None)

    @abstractmethod
    def get_directory(self, item: IEntity) -> Path:
        """Get the directory of the given entity."""
        pass

    @abstractmethod
    def get_directory_by_id(self, item_id: str, item_type: ItemType) -> Path:
        """Get the directory by item id."""
        pass

    @abstractmethod
    def make_command_executable(self, simulation: Simulation) -> None:
        """Make command executable."""
        pass

    @abstractmethod
    def mk_directory(self, item: IEntity, exist_ok: bool = False) -> None:
        """Make a new directory."""
        pass

    @abstractmethod
    def link_file(self, target: Union[Path, str], link: Union[Path, str]) -> None:
        """Link files with symlink."""
        pass

    @abstractmethod
    def link_dir(self, target: Union[Path, str], link: Union[Path, str]) -> None:
        """Link directory with symlink."""
        pass

    @abstractmethod
    def update_script_mode(self, script_path: Union[Path, str], mode: int) -> None:
        """Update script mode."""
        pass

    @abstractmethod
    def create_batch_file(self, item: IEntity, **kwargs) -> None:
        """Create batch file."""
        pass

    @abstractmethod
    def get_simulation_status(self, sim_id: str) -> Any:
        """Get simulation status."""
        pass

    @abstractmethod
    def create_file(self, file_path: str, content: str) -> None:
        """Create file."""
        pass
