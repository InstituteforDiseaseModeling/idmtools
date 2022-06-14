"""
Here we implement the SlurmPlatform simulation operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
# from pathlib import Path
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from typing import List, Dict, Type, Optional
from idmtools.assets import Asset
from idmtools.core import ItemType, EntityStatus
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.iplatform_ops.iplatform_simulation_operations import IPlatformSimulationOperations
from idmtools_platform_slurm.platform_operations.utils import SimulationDict, ExperimentDict, clean_experiment_name
from logging import getLogger

logger = getLogger(__name__)

# METADATA_FILE = 'metadata.json'


@dataclass
class SlurmPlatformSimulationOperations(IPlatformSimulationOperations):
    platform: 'SlurmPlatform'  # noqa: F821
    platform_type: Type = field(default=SimulationDict)

    def get(self, simulation_id: UUID, **kwargs) -> Dict:
        """
        Gets an simulation from the Slurm platform.
        Args:
            simulation_id: Simulation id
            kwargs: keyword arguments used to expand functionality
        Returns:
            Slurm Simulation object
        """
        # raise NotImplementedError("Fetching experiments has not been implemented on the Slurm Platform")

        # root = Path(self.platform.job_directory)
        # pattern = f'*/*/{simulation_id}/{METADATA_FILE}'
        # for meta_file in root.glob(pattern=pattern):
        #     # meta = self.platform._metas.load_bk(item_dir=meta_file.parent)
        #     meta = self.platform._metas.load_from_file(meta_file)
        #     return SimulationDict(meta)
        #
        # raise RuntimeError(f"Not found Simulation with id '{simulation_id}'")

        metas = self.platform._metas.filter(item_type=ItemType.SIMULATION, property_filter={'id': str(simulation_id)})
        if len(metas) > 0:
            return SimulationDict(metas[0])
        else:
            raise RuntimeError(f"Not found Simulation with id '{simulation_id}'")

    def platform_create(self, simulation: Simulation, **kwargs) -> Dict:
        """
        Create the simulation on Slurm Platform.
        Args:
            simulation: Simulation
            kwargs: keyword arguments used to expand functionality
        Returns:
            Slurm Simulation object created.
        """
        if not isinstance(simulation.uid, UUID):
            simulation.uid = uuid4()

        simulation.name = clean_experiment_name(simulation.experiment.name if not simulation.name else simulation.name)

        self.platform._op_client.mk_directory(simulation)
        self.platform._metas.dump(simulation)
        self.platform._assets.link_common_assets(simulation)
        self.platform._assets.dump_assets(simulation)
        self.platform._op_client.create_batch_file(simulation)

        meta = self.platform._metas.get(simulation)
        return SimulationDict(meta)

    def get_parent(self, simulation: SimulationDict, **kwargs) -> ExperimentDict:
        """
        Fetches the parent of a simulation.
        Args:
            simulation: Slurm Simulation
            kwargs: keyword arguments used to expand functionality
        Returns:
            The Experiment being the parent of this simulation.
        """
        # raise NotImplementedError("Get parent is not supported on Slurm Yet")

        if simulation.parent:
            return simulation.parent
        elif simulation.parent_id is None:
            return None
        else:
            return self.platform._experiments.get(simulation.parent_id, raw=True,
                                                  **kwargs) if simulation.experiment_id else None

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
        self.platform._metas.dump_assets(simulation, **kwargs)

    def refresh_status(self, simulation: Simulation, **kwargs):
        """
        Refresh status
        Args:
            simulation: idmtools Simulation
            kwargs: keyword arguments used to expand functionality
        Returns:
            None
        """
        raise NotImplementedError("Refresh status has not been implemented on the Slurm Platform")

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
        # raise NotImplementedError("Get assets has not been implemented on the Slurm Platform")

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
        # raise NotImplementedError("List assets has not been implemented on the Slurm Platform")

        ret = self.platform._assets.list_assets(simulation, **kwargs)
        return ret

    def to_entity(self, slurm_sim: Dict, parent: Optional[Experiment] = None, **kwargs) -> Simulation:
        """
        Convert a sim dict object to an ISimulation.

        Args:
            slurm_sim: simulation to convert
            parent: optional experiment object
            kwargs:
        Returns:
            Simulation object
        """
        if parent is None:
            parent = self.platform.get_item(slurm_sim["parent_id"], ItemType.EXPERIMENT, force=True)
        sim = Simulation(task=None)
        sim.platform = self.platform
        sim._uid = UUID(slurm_sim['uid'])
        # suite.uid = suite_meta['id']
        sim.name = slurm_sim['name']
        # simulation.experiment = parent
        # simulation.parent_id = local_sim["experiment_id"]
        sim.parent_id = parent.id  # may not need this
        sim.parent = parent
        sim.tags = slurm_sim['tags']
        sim._platform_object = slurm_sim
        sim.status = EntityStatus[slurm_sim['status']] if slurm_sim['status'] else EntityStatus.CREATED

        return sim
