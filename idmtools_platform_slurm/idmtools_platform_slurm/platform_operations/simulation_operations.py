import os
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from os import cpu_count
from pathlib import Path
from typing import List, Dict, Any, Tuple, Type
from uuid import UUID, uuid4

from jinja2 import Template

from idmtools.assets import Asset
from idmtools.entities.simulation import Simulation
from idmtools.entities.iplatform_ops.iplatform_simulation_operations import IPlatformSimulationOperations


@dataclass
class SlurmPlatformSimulationOperations(IPlatformSimulationOperations):

    platform: 'SlurmPlatform'  # noqa: F821
    platform_type: Type = Simulation

    def get(self, simulation_id: UUID, **kwargs) -> Any:
        """
        Get our simulation.

        TODO: How do we do this? By id? By directory? eek?
        Args:
            simulation_id:
            **kwargs:

        Returns:

        """
        raise NotImplementedError("Fetching experiments has not been implemented on the Slurm Platform")

    def platform_create(self, simulation: Simulation, common_asset_dir=None) -> Tuple[Any, UUID]:
        """
        Create the simulation on Slurm.

        Here we need to create directory
        Copy our files
        Prep our script

        Args:
            simulation:
            common_asset_dir:

        Returns:

        """
        if common_asset_dir is None:
            common_asset_dir = os.path.join(self.platform.job_directory, simulation.experiment.uid, 'Assets')
        simulation.uid = str(uuid4())
        self.platform.metadata_ops.save(simulation)
        sim_dir = Path(self.platform.job_directory, simulation.experiment.uid, simulation.uid)
        self.platform._op_client.mk_directory(sim_dir)
        # store sim info in folder
        self.platform._op_client.dump_metadata(simulation, os.path.join(sim_dir, 'simulation.json'))
        self.platform._op_client.link_dir(common_asset_dir, os.path.join(sim_dir, 'Assets'))
        self.send_assets(simulation, )
        # TODO Move this to ops somehow? Maybe through assets earlier in process
        sim_script = sim_dir.joinpath("_run.sh")
        with open(sim_script, "w") as tout:
            with open(Path(__file__).parent.parent.joinpath("assets/_run.sh.jinja2")) as tin:
                t = Template(tin.read())
                tout.write(t.render(simulation=simulation))
        # TODO Add this command to ops
        sim_script.chmod(0o755)
        return simulation, simulation.uid

    def get_parent(self, simulation: Any, **kwargs) -> Any:
        """
        Fetches the parent of a simulation.

        TODO: Leverage asset service. Some open questions here is do we need directory?

        Args:
            simulation:
            **kwargs:

        Returns:

        """
        raise NotImplementedError("Listing assets is not supported on Slurm Yet")

    def batch_create(self, sims: List[Simulation], **kwargs) -> List[Tuple[Any, UUID]]:
        """
        Creates a set of simulation.

        TODO: Look at performance later
        Args:
            sims:
            **kwargs:

        Returns:

        """
        created = []
        # common_asset_dir = os.path.join(self.platform.job_directory, sims[0].experiment.uid, 'Assets')

        for simulation in sims:
            created.append(self.create(simulation))
        return created

    def run_item(self, simulation: Simulation, **kwargs):
        """
        Run item

        Args:
            simulation: Simulation
            **kwargs:

        Returns:

        """
        pass

    def send_assets(self, simulation: Simulation, **kwargs):
        """
        Send assets.

        TODO: Move logic to asset interface

        Args:
            simulation:
            **kwargs:

        Returns:

        """
        for asset in simulation.assets:
            sim_dir = os.path.join(self.platform.job_directory, simulation.experiment.uid, simulation.uid)
            self.platform._op_client.copy_asset(asset, sim_dir)

    def refresh_status(self, simulation: Simulation, **kwargs):
        """
        Refresh status
        TODO: Leverage metadata

        Args:
            simulation:
            **kwargs:

        Returns:

        """
        raise NotImplementedError("Fetching experiments has not been implemented on the Slurm Platform")

    def get_assets(self, simulation: Simulation, files: List[str], **kwargs) -> Dict[str, bytearray]:
        """
        Get assets for simulation.

        TODO: Leverage asset service
        Args:
            simulation:
            files:
            **kwargs:

        Returns:

        """
        ret = dict()
        futures = {}
        base_path = os.path.join(self.platform.job_directory, simulation.experiment.uid, simulation.uid)
        with ThreadPoolExecutor(max_workers=cpu_count()) as pool:
            for file in files:
                futures[pool.submit(self.platform._op_client.download_asset, os.path.join(file, base_path))] = file

            for future in as_completed(futures):
                ret[futures[future]] = future.result()
        return ret

    def list_assets(self, simulation: Simulation, **kwargs) -> List[str]:
        """
        List assets for simulation.

        Args:
            simulation:
            **kwargs:

        Returns:

        """
        raise NotImplementedError("Listing assets is not supported on Slurm Yet")

    def platform_run_item(self, simulation: Simulation, **kwargs):
        """
        For simulations on slurm, we let the experiment execute with sbatch

        Args:
            simulation:
            **kwargs:

        Returns:

        """
        pass

    def list_files(self, simulation: Simulation, **kwargs) -> List[Asset]:
        """
        List files for simulation.

        Args:
            simulation:
            **kwargs:

        Returns:

        """
        raise NotImplementedError("Listing files is not supported on Slurm Yet")
