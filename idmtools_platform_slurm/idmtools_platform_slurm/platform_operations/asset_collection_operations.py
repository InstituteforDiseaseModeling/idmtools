"""
Here we implement the SlurmPlatform asset collection operations.

Copyright 2025, Gates Foundation. All rights reserved.
"""
from dataclasses import field, dataclass
from logging import getLogger
from typing import TYPE_CHECKING, Type, List, Dict, Union
from idmtools.core import ItemType
from idmtools.entities.simulation import Simulation
from idmtools_platform_file.platform_operations.asset_collection_operations import FilePlatformAssetCollectionOperations
from idmtools_platform_file.platform_operations.utils import FileSimulation

if TYPE_CHECKING:
    from idmtools_platform_slurm.slurm_platform import SlurmPlatform

logger = getLogger(__name__)
user_logger = getLogger("user")

EXCLUDE_FILES = ['_run.sh', 'metadata.json', 'stdout.txt', 'stderr.txt', 'status.txt', 'job_id.txt', 'job_status.txt']


@dataclass
class SlurmPlatformAssetCollectionOperations(FilePlatformAssetCollectionOperations):
    """
    Provides AssetCollection Operations to SlurmPlatform.
    """
    platform: 'SlurmPlatform'  # noqa F821
    platform_type: Type = field(default=None)

    def get_assets(self, simulation: Union[Simulation, FileSimulation], files: List[str], **kwargs) -> Dict[
        str, bytearray]:
        """
        Get assets for simulation.
        Args:
            simulation: Simulation or SlurmSimulation
            files: files to be retrieved
            kwargs: keyword arguments used to expand functionality.
        Returns:
            Dict[str, bytearray]
        """
        if isinstance(simulation, (Simulation, FileSimulation)):
            sim_dir = self.platform.get_directory_by_id(simulation.id, ItemType.SIMULATION)
            return self._get_assets_from_dir(sim_dir, files)
        else:
            raise NotImplementedError(
                f"get_assets() for items of type {type(simulation)} is not supported on SlurmPlatform.")
