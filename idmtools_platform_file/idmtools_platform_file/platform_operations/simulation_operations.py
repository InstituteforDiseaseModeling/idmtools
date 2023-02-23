"""
Here we implement the FilePlatform simulation operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import shutil
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Dict, Type, Optional, Union, Any
from idmtools.assets import Asset
from idmtools.core import ItemType
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.iplatform_ops.iplatform_simulation_operations import IPlatformSimulationOperations
from idmtools_platform_file.utils import FileSimulation, FileExperiment, clean_experiment_name
from logging import getLogger

logger = getLogger(__name__)
user_logger = getLogger('user')

if TYPE_CHECKING:
    from idmtools_platform_file.file_platform import FilePlatform

logger = getLogger(__name__)


@dataclass
class FilePlatformSimulationOperations(IPlatformSimulationOperations):
    """
    Simulation Operation for File Platform.
    """
    platform: 'FilePlatform'  # noqa: F821
    platform_type: Type = field(default=FileSimulation)

    def get(self, simulation_id: str, **kwargs) -> Dict:
        """
        Gets a simulation from the File platform.
        Args:
            simulation_id: Simulation id
            kwargs: keyword arguments used to expand functionality
        Returns:
            File Simulation object
        """
        metas = self.platform._metas.filter(item_type=ItemType.SIMULATION, property_filter={'id': str(simulation_id)})
        if len(metas) > 0:
            # update status - data analysis may need this
            file_sim = FileSimulation(metas[0])
            file_sim.status = self.platform.get_simulation_status(file_sim.id)
            return file_sim
        else:
            raise RuntimeError(f"Not found Simulation with id '{simulation_id}'")

    def platform_create(self, simulation: Simulation, **kwargs) -> FileSimulation:
        """
        Create the simulation on File Platform.
        Args:
            simulation: Simulation
            kwargs: keyword arguments used to expand functionality
        Returns:
            File Simulation object created.
        """
        simulation.name = clean_experiment_name(simulation.experiment.name if not simulation.name else simulation.name)

        # Generate Simulation folder structure
        self.platform.mk_directory(simulation)
        meta = self.platform._metas.dump(simulation)
        self.platform._assets.link_common_assets(simulation)
        self.platform._assets.dump_assets(simulation)
        self.platform.create_batch_file(simulation, **kwargs)

        # Make command executable
        self.platform.make_command_executable(simulation)

        # Return File Simulation
        file_sim = FileSimulation(meta)
        return file_sim

    def get_parent(self, simulation: FileSimulation, **kwargs) -> FileExperiment:
        """
        Fetches the parent of a simulation.
        Args:
            simulation: File Simulation
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
        For simulations on file, we let the experiment execute with batch.
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

    def to_entity(self, file_sim: FileSimulation, parent: Optional[Experiment] = None, **kwargs) -> Simulation:
        """
        Convert a FileSimulation object to idmtools Simulation.

        Args:
            file_sim: simulation to convert
            parent: optional experiment object
            kwargs: keyword arguments used to expand functionality
        Returns:
            Simulation object
        """
        if parent is None:
            parent = self.platform.get_item(file_sim.parent_id, ItemType.EXPERIMENT, force=True)
        sim = Simulation(task=None)
        sim.platform = self.platform
        sim.uid = file_sim.uid
        sim.name = file_sim.name
        sim.parent_id = parent.id
        sim.parent = parent
        sim.tags = file_sim.tags
        sim._platform_object = file_sim
        # Convert status
        sim.status = file_sim.status

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
        raise NotImplementedError("Refresh simulation status is not called directly on the File Platform")

    def create_sim_directory_map(self, simulation_id: str) -> Dict:
        """
        Build simulation working directory mapping.
        Args:
            simulation_id: simulation id

        Returns:
            Dict of simulation id as key and working dir as value
        """
        sim = self.platform.get_item(simulation_id, ItemType.SIMULATION, raw=False)
        return {sim.id: str(self.platform.get_directory_by_id(simulation_id, ItemType.SIMULATION))}

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
            shutil.rmtree(self.platform.get_directory(sim))
        except RuntimeError:
            logger.info(f"Could not delete the simulation: {sim_id}..")
            return

    def platform_cancel(self, sim_id: str, force: bool = False) -> Any:
        """
        Cancel platform simulation's file job.
        Args:
            sim_id: simulation id
            force: bool, True/False
        Returns:
            Any
        """
        pass
