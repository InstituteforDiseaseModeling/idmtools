"""
Here we implement the SlurmPlatform remote operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Union, Any

from idmtools.core import ItemType
from idmtools.core.interfaces.ientity import IEntity
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools_platform_slurm.slurm_operations.operations_interface import SlurmOperations


@dataclass
class RemoteSlurmOperations(SlurmOperations):
    hostname: str = field(default=None)
    username: str = field(default=None)
    key_file: str = field(default=None)
    port: int = field(default=22)

    def get_directory(self, item: IEntity) -> Path:
        pass

    def get_directory_by_id(self, item_id: str, item_type: ItemType) -> Path:
        pass

    def mk_directory(self, item: IEntity) -> None:
        pass

    def link_file(self, target: Union[Path, str], link: Union[Path, str]) -> None:
        pass

    def link_dir(self, target: Union[Path, str], link: Union[Path, str]) -> None:
        pass

    def update_script_mode(self, script_path: Union[Path, str], mode: int) -> None:
        pass

    def make_command_executable(self, simulation: Simulation) -> None:
        pass

    def create_batch_file(self, item: IEntity, **kwargs) -> None:
        pass

    def submit_job(self, item: Union[Experiment, Simulation], **kwargs) -> Any:
        pass

    def get_simulation_status(self, sim_id: Union[str]) -> Any:
        pass
