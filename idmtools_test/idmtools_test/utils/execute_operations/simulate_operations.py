import json
import os
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from functools import partial
from logging import getLogger, DEBUG
from threading import Lock
from typing import List, Dict, Any, Type, TYPE_CHECKING, Union
from uuid import UUID, uuid4
import numpy as np
from idmtools.assets import Asset
from idmtools.core import EntityStatus
from idmtools.entities.iplatform_ops.iplatform_simulation_operations import IPlatformSimulationOperations
from idmtools.entities.simulation import Simulation
from idmtools.utils.file import file_contents_to_generator
from idmtools.utils.json import IDMJSONEncoder

if TYPE_CHECKING:
    from idmtools_test.utils.test_execute_platform import TestExecutePlatform

current_directory = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.abspath(os.path.join(current_directory, "..", "..", "data"))

logger = getLogger(__name__)
SIMULATION_LOCK = Lock()


def run_simulation(simulation_id: Simulation, command: str, parent_uid: UUID, execute_directory):
    simulation_path = os.path.join(execute_directory, str(parent_uid), str(simulation_id))
    os.makedirs(simulation_path, exist_ok=True)
    with open(os.path.join(simulation_path, "StdOut.txt"), "w") as out, \
            open(os.path.join(simulation_path, "StdErr.txt"), "w") as err:
        try:
            cmd = str(command)
            logger.info('Executing %s from working directory %s', cmd, simulation_path)
            err.write(f"{cmd}\n")

            os.chdir(simulation_path)
            # Run our task
            if sys.platform in ['win32', 'cygwin']:
                cmd = shlex.split(cmd.replace("\\", "/"))
                cmd[0] = os.path.abspath(cmd[0])
                cmd = subprocess.list2cmdline(cmd)
            else:
                cmd = shlex.split(cmd.replace("\\", "/"))
            p = subprocess.Popen(
                cmd,
                cwd=simulation_path,
                env=os.environ,
                shell=False,
                stdout=out,
                stderr=err
            )
            # store the pid in case we want to cancel later
            logger.info(f"Process id: {p.pid}")
            # Log that we have started this particular simulation
            p.wait()
            if p.returncode == 0:
                status = EntityStatus.SUCCEEDED
            else:
                status = EntityStatus.FAILED
        except Exception as e:
            logger.exception(e)
            err.write(str(e))
            status = EntityStatus.FAILED
    return parent_uid, simulation_id, status


@dataclass
class TestExecutePlatformSimulationOperation(IPlatformSimulationOperations):
    platform: 'TestExecutePlatform'

    def all_files(self, simulation: Simulation, **kwargs):
        pass

    platform_type: Type = Simulation
    simulations: dict = field(default_factory=dict, compare=False, metadata={"pickle_ignore": True})

    def get(self, simulation_id: UUID, **kwargs) -> Any:
        obj = None
        for eid in self.simulations:
            sims = self.simulations.get(eid)
            if sims:
                for sim in self.simulations.get(eid):
                    if sim.uid == simulation_id:
                        obj = sim
                        break
            if obj:
                break
        obj.platform = self.platform
        return obj

    def platform_create(self, simulation: Simulation, **kwargs) -> Simulation:
        simulation.platform = self
        experiment_id = simulation.parent_id
        simulation.uid = uuid4()

        self._save_simulations_to_cache(experiment_id, [simulation])
        return simulation

    def _save_simulations_to_cache(self, experiment_id, simulations: List[Simulation], overwrite: bool = False):
        if logger.isEnabledFor(DEBUG):
            logger.debug(f'Saving {len(simulations)} to Experiment {experiment_id}')
        SIMULATION_LOCK.acquire()
        existing_simulations = [] if overwrite else self.simulations.pop(experiment_id)
        self.simulations[experiment_id] = existing_simulations + simulations
        SIMULATION_LOCK.release()
        logger.debug(f'Saved sims')

    def batch_create(self, sims: List[Simulation], **kwargs) -> List[Simulation]:

        simulations = []
        experiment_id = None
        for simulation in sims:
            if simulation.status is None:
                self.pre_create(simulation)
                experiment_id = simulation.parent_id
                simulation.uid = uuid4()
                exp_path = os.path.join(self.platform.execute_directory, str(experiment_id))
                sim_path = os.path.join(exp_path, str(simulation.id))
                os.makedirs(sim_path, exist_ok=True)
                with open(os.path.join(sim_path, "simulation_metadata.json"), 'w') as out:
                    out.write(json.dumps(simulation.to_dict(), cls=IDMJSONEncoder))
                self.post_create(simulation)
                simulations.append(simulation)

        if experiment_id:
            self._save_simulations_to_cache(experiment_id, simulations)
        return simulations

    def get_parent(self, simulation: Any, **kwargs) -> Any:
        return self.platform._experiments.experiments.get(simulation.parent_id)

    def platform_run_item(self, simulation: Simulation, **kwargs):
        """
        Run the item on the test platform

        This method executes the simulation in a thread pool

        Args:
            simulation: Simulation to run
            **kwargs:

        Returns:

        """
        logger.info(f"Running simulation {simulation.id}")
        self.send_assets(simulation, **kwargs)
        future = self.platform.pool.submit(
            run_simulation,
            simulation.id,
            simulation.task.command,
            simulation.parent.uid,
            self.platform.execute_directory
        )
        sims = self.simulations[simulation.parent.uid]

        for i, sim in enumerate(sims):
            if sim.id == simulation.id:
                sims[i] = simulation
                self._save_simulations_to_cache(simulation.parent.uid, sims)
                break
        self.platform.queue.append(future)

    def send_assets(self, simulation: Any, **kwargs):
        """
        Send assets to the test platform. This method uses the execute directory and first tries to link files
        If that fails, files are copied into the directory

        Args:
            simulation: Simulation assets to send
            **kwargs:

        Returns:

        """
        exp_path = self.platform._experiments.get_experiment_path(simulation.parent)
        sim_path = self.get_simulation_asset_path(simulation, experiment_path=exp_path)
        logger.info(f"Creating {exp_path}")
        os.makedirs(sim_path, exist_ok=True)
        self.__copy_simulation_assets_to_simulation_directory(sim_path, simulation)
        exp_path = os.path.join(exp_path, "Assets")
        self._copy_or_link_parent_assets(exp_path, sim_path, simulation)

    def get_simulation_asset_path(self, simulation: Simulation, experiment_path: str = None) -> str:
        """
        Get path to simulation assets

        Args:
            simulation: Simulation Assets to get path to

        Returns:
            Str path to assets
        """
        if experiment_path is None:
            experiment_path = self.platform._experiments.get_experiment_path(simulation.parent)
        return os.path.join(experiment_path, str(simulation.id))

    @staticmethod
    def _copy_or_link_parent_assets(exp_path: str, sim_path: str, simulation: Simulation):
        """
        Link or Copy a simulation parent assets into its directory

        Args:
            exp_path: Path to experiment assets
            sim_path: Simulation path
            simulation: Simulation

        Returns:

        """
        for asset in simulation.parent.assets:
            remote_path = os.path.join(exp_path, asset.relative_path) if asset.relative_path else exp_path
            sim_assets = os.path.join(sim_path, "Assets")
            src_path = os.path.join(remote_path, asset.filename)
            dest_path = os.path.join(sim_assets, asset.filename)
            os.makedirs(sim_assets, exist_ok=True)
            if sys.platform in ['win32']:
                import win32file
                link_worked = True
                try:
                    logger.info("Trying to link the files")
                    if link_worked:
                        win32file.CreateSymbolicLink(src_path, dest_path, 1)
                    else:
                        shutil.copy(src_path, dest_path)
                except Exception:
                    link_worked = False
                    logger.info("Linking failed. Copying instread")
                    shutil.copy(src_path, dest_path)
            else:
                os.symlink(src_path, dest_path)

    @staticmethod
    def __copy_simulation_assets_to_simulation_directory(sim_path:str, simulation: Simulation):
        for asset in simulation.assets:
            remote_path = os.path.join(sim_path, asset.relative_path) if asset.relative_path else sim_path
            remote_path = os.path.join(remote_path, asset.filename)
            if asset.absolute_path:
                logger.info(f"Copying {asset.absolute_path} to {remote_path}")
                shutil.copy(asset.absolute_path, remote_path)
            else:
                logger.info(f"Writing {asset.absolute_path} to {remote_path}")
                with open(os.path.join(remote_path), 'wb') as out:
                    out.write(asset.content.encode())

    def refresh_status(self, simulation: Simulation, **kwargs):
        pass

    def get_assets(self, simulation: Simulation, files: List[str], **kwargs) -> Dict[str, bytearray]:
        """
        Get list of files
        Args:
            simulation:
            files:
            **kwargs:

        Returns:

        """
        logger.info(f'Listing assets for {simulation.id}')
        assets = {}
        for root, dirs, actual_files in os.walk(self.get_simulation_asset_path(simulation)):
            for file in actual_files:
                if file in files:
                    fp = os.path.abspath(os.path.join(root, file))
                    with open(fp, 'rb') as i:
                        assets[file] = i.read()
        return assets

    def list_assets(self, simulation: Simulation, **kwargs) -> List[Asset]:
        """
        List assets for an item

        Args:
            simulation: Simulation to list assets for
            **kwargs:

        Returns:

        """
        logger.info(f'Listing assets for {simulation.id}')
        assets = []
        for root, dirs, files in os.walk(self.get_simulation_asset_path(simulation)):
            for file in files:
                fp = os.path.abspath(os.path.join(root, file))
                asset = Asset(absolute_path=fp, filename=file)
                asset.download_generator_hook = partial(file_contents_to_generator, fp)
                assets.append(asset)
        return assets



