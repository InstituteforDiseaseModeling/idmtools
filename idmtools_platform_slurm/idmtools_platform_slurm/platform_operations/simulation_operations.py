"""
Here we implement the SlurmPlatform simulation operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Dict, Type, Optional, Union, Any
import shutil
from idmtools.assets import Asset
from idmtools.core import ItemType, EntityStatus
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.iplatform_ops.iplatform_simulation_operations import IPlatformSimulationOperations
from idmtools_platform_slurm.platform_operations.utils import SlurmSimulation, SlurmExperiment, clean_experiment_name
from logging import getLogger

logger = getLogger(__name__)
user_logger = getLogger('user')

if TYPE_CHECKING:
    from idmtools_platform_slurm.slurm_platform import SlurmPlatform

logger = getLogger(__name__)


@dataclass
class SlurmPlatformSimulationOperations(IPlatformSimulationOperations):
    platform: 'SlurmPlatform'  # noqa: F821
    platform_type: Type = field(default=SlurmSimulation)

    def get(self, simulation_id: str, **kwargs) -> Dict:
        """
        Gets a simulation from the Slurm platform.
        Args:
            simulation_id: Simulation id
            kwargs: keyword arguments used to expand functionality
        Returns:
            Slurm Simulation object
        """
        metas = self.platform._metas.filter(item_type=ItemType.SIMULATION, property_filter={'id': str(simulation_id)})
        if len(metas) > 0:
            # update status - data analysis may need this
            slurm_sim = SlurmSimulation(metas[0])
            slurm_sim.status = self.platform._op_client.get_simulation_status(slurm_sim.id)
            return slurm_sim
        else:
            raise RuntimeError(f"Not found Simulation with id '{simulation_id}'")

    def platform_create(self, simulation: Simulation, **kwargs) -> SlurmSimulation:
        """
        Create the simulation on Slurm Platform.
        Args:
            simulation: Simulation
            kwargs: keyword arguments used to expand functionality
        Returns:
            Slurm Simulation object created.
        """
        simulation.name = clean_experiment_name(simulation.experiment.name if not simulation.name else simulation.name)

        # Generate Simulation folder structure
        self.platform._op_client.mk_directory(simulation, exist_ok=False)
        meta = self.platform._metas.dump(simulation)
        # self.platform._assets.link_common_assets(simulation)
        self.platform._assets.dump_assets(simulation)
        self.platform._op_client.create_batch_file(simulation, **kwargs)

        # Make command executable
        self.platform._op_client.make_command_executable(simulation)

        # Return Slurm Simulation
        slurm_sim = SlurmSimulation(meta)
        return slurm_sim

    def get_parent(self, simulation: SlurmSimulation, **kwargs) -> SlurmExperiment:
        """
        Fetches the parent of a simulation.
        Args:
            simulation: Slurm Simulation
            kwargs: keyword arguments used to expand functionality
        Returns:
            The Experiment being the parent of this simulation.
        """
        if simulation.parent_id is None:
            return None
        else:
            return self.platform._experiments.get(simulation.parent_id, raw=True, **kwargs)

    def platform_run_item(self, simulation: Simulation, **kwargs):
        """
        For simulations on slurm, we let the experiment execute with sbatch
        Args:
            simulation: idmtools Simulation
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
            simulation: idmtools Simulation
            kwargs: keyword arguments used to expand functionality
        Returns:
            None
        """
        pass

    def get_assets(self, simulation: Simulation, files: List[str], **kwargs) -> Dict[str, bytearray]:
        """
        Get assets for simulation.
        Args:
            simulation: idmtools Simulation
            files: files to be retrieved
            kwargs: keyword arguments used to expand functionality
        Returns:
            Dict[str, bytearray]
        """
        ret = self.platform._assets.get_assets(simulation, files, **kwargs)
        return ret

    def list_assets(self, simulation: Simulation, **kwargs) -> List[Asset]:
        """
        List assets for simulation.
        Args:
            simulation: idmtools Simulation
            kwargs: keyword arguments used to expand functionality
        Returns:
            List[Asset]
        """
        ret = self.platform._assets.list_assets(simulation, **kwargs)
        return ret

    def to_entity(self, slurm_sim: SlurmSimulation, parent: Optional[Experiment] = None, **kwargs) -> Simulation:
        """
        Convert a SlurmSimulation object to idmtools Simulation.

        Args:
            slurm_sim: simulation to convert
            parent: optional experiment object
            kwargs: keyword arguments used to expand functionality
        Returns:
            Simulation object
        """
        if parent is None:
            parent = self.platform.get_item(slurm_sim.parent_id, ItemType.EXPERIMENT, force=True)
        sim = Simulation(task=None)
        sim.platform = self.platform
        sim.uid = slurm_sim.uid
        sim.name = slurm_sim.name
        sim.parent_id = parent.id
        sim.parent = parent
        sim.tags = slurm_sim.tags
        sim._platform_object = slurm_sim
        # Convert status
        sim.status = slurm_sim.status

        return sim

    def refresh_status(self, simulation: Simulation, **kwargs):
        """
        Refresh simulation status: we actually don't really refresh simulation' status directly.
        Args:
            simulation: idmtools Simulation
            kwargs: keyword arguments used to expand functionality
        Returns:
            None
        """
        raise NotImplementedError("Refresh simulation status is not called directly on the Slurm Platform")

    def create_sim_directory_map(self, simulation_id: str) -> Dict:
        """
        Build simulation working directory mapping.
        Args:
            simulation_id: simulation id

        Returns:
            Dict of simulation id as key and working dir as value
        """
        sim = self.platform.get_item(simulation_id, ItemType.SIMULATION, raw=False)
        return {sim.id: str(self.platform._op_client.get_directory_by_id(simulation_id, ItemType.SIMULATION))}

    def platform_delete(self, sim_id: str) -> None:
        """
        Delete platform simulation.
        Args:
            sim_id: platform simulation id
        Returns:
            None
        """
        sim = self.platform.get_item(sim_id, ItemType.SIMULATION, raw=False)
        try:
            shutil.rmtree(self.platform._op_client.get_directory(sim))
        except RuntimeError:
            logger.info(f"Could not delete the simulation: {sim_id}..")
            return

    def platform_cancel(self, sim_id: str, force: bool = False) -> Any:
        """
        Cancel platform simulation's slurm job.
        Args:
            sim_id: simulation id
            force: bool, True/False
        Returns:
            Any
        """
        sim = self.platform.get_item(sim_id, ItemType.SIMULATION, raw=False)
        if force or sim.status == EntityStatus.RUNNING:
            logger.debug(f"cancel slurm job for simulation: {sim_id}...")
            job_id = self.platform._op_client.get_job_id(sim_id, ItemType.SIMULATION)
            if job_id is None:
                logger.debug(f"Slurm job for simulation: {sim_id} is not available!")
                return
            else:
                result = self.platform._op_client.cancel_job(job_id)
                user_logger.info(f"Cancel Simulation: {sim_id}: {result}")
                return result
        else:
            user_logger.info(f"Simulation {sim_id} is not running, no cancel needed...")
