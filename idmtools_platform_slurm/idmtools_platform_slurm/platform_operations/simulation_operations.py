"""
Here we implement the SlurmPlatform simulation operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from pathlib import Path
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from typing import List, Dict, Any, Type, Optional
from idmtools.assets import Asset
from idmtools.core import ItemType, EntityStatus
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.iplatform_ops.iplatform_simulation_operations import IPlatformSimulationOperations
from idmtools_platform_slurm.platform_operations.utils import SimulationDict, clean_experiment_name
from logging import getLogger, DEBUG

logger = getLogger(__name__)


@dataclass
class SlurmPlatformSimulationOperations(IPlatformSimulationOperations):
    platform: 'SlurmPlatform'  # noqa: F821
    platform_type: Type = field(default=SimulationDict)

    def get(self, simulation_id: UUID, **kwargs) -> Dict:
        """
        Get our simulation.
        Args:
            simulation_id: Simulation id
            kwargs: keyword arguments used to expand functionality
        Returns:
            Simulation expected.
        """
        raise NotImplementedError("Fetching experiments has not been implemented on the Slurm Platform")

    def platform_create(self, simulation: Simulation, **kwargs) -> Dict:
        """
        Create the simulation on Slurm Platform.
        Args:
            simulation: Simulation
            kwargs: keyword arguments used to expand functionality
        Returns:
            Simulation created.
        """
        if not isinstance(simulation.uid, UUID):
            simulation.uid = uuid4()

        simulation.name = clean_experiment_name(simulation.experiment.name if not simulation.name else simulation.name)

        self.platform._op_client.mk_directory(simulation)
        self.platform._metas.dump(simulation)
        self.platform._assets.link_common_assets(simulation)
        self.platform._assets.dump_assets(simulation)
        # TODO: may not need this
        self.platform._op_client.create_batch_file(simulation)

        meta = self.platform._metas.get(simulation)
        return SimulationDict(meta)

    def get_parent(self, simulation: Simulation, **kwargs) -> Any:
        """
        Fetches the parent of a simulation.
        Args:
            simulation: Simulation
            kwargs: keyword arguments used to expand functionality
        Returns:
            The Experiment being the parent of this simulation.
        """
        raise NotImplementedError("Get parent is not supported on Slurm Yet")

    def platform_run_item(self, simulation: Simulation, **kwargs):
        """
        For simulations on slurm, we let the experiment execute with sbatch
        Args:
            simulation: Simulation
            kwargs: keyword arguments used to expand functionality
        Returns:
            None
        """
        pass

    def send_assets(self, simulation: Simulation, **kwargs):
        """
        Send assets.
        Replaced by self.platform._metas.dump(simulation)
        Args:
            simulation: Simulation
            kwargs: keyword arguments used to expand functionality
        Returns:
            None
        """
        pass

    def refresh_status(self, simulation: Simulation, **kwargs):
        """
        Refresh status
        Args:
            simulation: Simulation
            kwargs: keyword arguments used to expand functionality
        Returns:
            None
        """
        raise NotImplementedError("Refresh status has not been implemented on the Slurm Platform")

    def get_assets(self, simulation: Simulation, files: List[str], **kwargs) -> Dict[str, bytearray]:
        """
        Get assets for simulation.
        Args:
            simulation: Simulation
            files: files to be retrieved
            kwargs: keyword arguments used to expand functionality
        Returns:
            Dict[str, bytearray]
        """
        raise NotImplementedError("Get assets has not been implemented on the Slurm Platform")

    def list_assets(self, simulation: Simulation, **kwargs) -> List[Asset]:
        """
        List assets for simulation.
        Args:
            simulation: Simulation
            kwargs: keyword arguments used to expand functionality
        Returns:
            List[Asset]
        """
        raise NotImplementedError("List assets has not been implemented on the Slurm Platform")
