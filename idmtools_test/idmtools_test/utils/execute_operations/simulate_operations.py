import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from functools import partial
from logging import getLogger
from pathlib import Path
from threading import Lock
from typing import List, Dict, Any, Type, TYPE_CHECKING, Optional
from uuid import UUID, uuid4
from idmtools.assets import Asset, AssetCollection
from idmtools.core import EntityStatus
from idmtools.core.task_factory import TaskFactory
from idmtools.entities import CommandLine
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform_ops.iplatform_simulation_operations import IPlatformSimulationOperations
from idmtools.entities.simulation import Simulation
from idmtools.utils.file import file_contents_to_generator
from idmtools.utils.json import IDMJSONEncoder

if TYPE_CHECKING:  # pragma: no cover
    from idmtools_test.utils.test_execute_platform import TestExecutePlatform

current_directory = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.abspath(os.path.join(current_directory, "..", "..", "data"))

logger = getLogger(__name__)
SIMULATION_LOCK = Lock()


class SimulationDict(dict):
    pass


def run_simulation(simulation_id: Simulation, command: str, parent_uid: UUID, execute_directory, shell: bool = False):
    simulation_path = os.path.join(execute_directory, str(parent_uid), str(simulation_id))
    os.makedirs(simulation_path, exist_ok=True)
    with open(os.path.join(simulation_path, "StdOut.txt"), "w") as out, \
            open(os.path.join(simulation_path, "StdErr.txt"), "w") as err:
        try:
            cmd = str(command)
            print(cmd)
            print(execute_directory)
            if cmd.startswith(execute_directory):
                cmd = cmd.replace(execute_directory, "")
            logger.info('Executing %s from working directory %s', cmd, simulation_path)
            err.write(f"{cmd}\n")

            # Run our task
            if sys.platform in ['win32', 'cygwin']:
                cmd = shlex.split(cmd.replace("\\", "/"))
                if os.path.exists(os.path.join(simulation_path, cmd[0])):
                    cmd[0] = os.path.join(simulation_path, cmd[0])
                else:
                    cmd[0] = os.path.abspath(cmd[0])
                cmd = subprocess.list2cmdline(cmd)
            else:
                cmd = shlex.split(cmd.replace("\\", "/"))
                try:
                    if not os.access(cmd[0], os.X_OK):
                        os.chmod(cmd[0], 0o777)
                except:
                    pass
            logger.info(cmd)
            if cmd[0].endswith(".sh"):
                cmd.insert(0, "/bin/bash")
            p = subprocess.Popen(
                cmd,
                cwd=simulation_path,
                env=os.environ,
                shell=shell,
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
    platform_type: Type = SimulationDict

    def get(self, simulation_id: UUID, experiment_id: UUID = None, **kwargs) -> Any:
        if simulation_id and experiment_id:
            exp_path = os.path.join(self.platform.execute_directory, str(experiment_id))
            sim_path = os.path.join(exp_path, str(simulation_id))
            metadata_src = os.path.join(sim_path, "simulation_metadata.json")
            if not os.path.exists(metadata_src):
                logger.error("Cannot find the simulation at {metadata}")
                raise ValueError(f"Cannot find the simulation at {metadata_src}")
            with open(metadata_src, 'r') as metadata_in:
                metadata = json.load(metadata_in)
                return SimulationDict(metadata)

    def platform_create(self, simulation: Simulation, **kwargs) -> Simulation:
        simulation.platform = self
        experiment_id = simulation.parent_id
        self.save_metadata(simulation)
        return simulation

    def batch_create(self, sims: List[Simulation], **kwargs) -> List[Simulation]:

        simulations = []
        experiment_id = None
        for simulation in sims:
            if simulation.status is None:
                self.pre_create(simulation, **kwargs)
                experiment_id = simulation.parent_id
                self.save_metadata(simulation)
                self.post_create(simulation, **kwargs)
                simulations.append(simulation)
            else:
                simulations.append(simulation)
        return simulations

    def save_metadata(self, simulation: Simulation, update_data: dict = None):
        exp_path = os.path.join(self.platform.execute_directory, str(simulation.parent_id))
        sim_path = os.path.join(exp_path, str(simulation.id))
        metadata_file = os.path.join(sim_path, "simulation_metadata.json")
        os.makedirs(sim_path, exist_ok=True)
        if update_data and os.path.exists(metadata_file):
            with open(metadata_file, 'r') as metadata_src:
                metadata = json.load(metadata_src)
                metadata.update(update_data)
        else:
            metadata = simulation.to_dict()

        with open(metadata_file, 'w') as out:
            out.write(json.dumps(metadata, cls=IDMJSONEncoder))

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
        exp_path = self.platform._experiments.get_experiment_path(simulation.parent.uid)
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
            experiment_path = self.platform._experiments.get_experiment_path(simulation.parent.uid)
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
            remote_path = Path(exp_path).joinpath(asset.relative_path) if asset.relative_path else Path(exp_path)
            sim_assets = Path(sim_path).joinpath("Assets")
            src_path = remote_path.joinpath(asset.filename)
            dest_path = sim_assets.joinpath(asset.filename)
            sim_assets.mkdir(parents=True, exist_ok=True)
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
                cksum_hash = hashlib.md5()
                with open(fp, 'rb') as fin:
                    cksum_hash.update(fin.read())
                    asset.checksum = cksum_hash.hexdigest()
                assets.append(asset)
        return assets

    def to_entity(self, dict_sim: Dict, load_task: bool = False, parent: Optional[Experiment] = None,
                  **kwargs) -> Simulation:
        # convert the dictionary to simulation
        sim: Simulation = Simulation(**{k: v for k, v in dict_sim.items() if k not in ['platform_id', 'item_type']})
        try:
            # load status from str
            sim.status = EntityStatus[sim.status.upper()]
        except:
            pass
        # set platform before we load assets
        sim.platform = self.platform
        # and our parent
        if parent:
            sim.parent = parent
        # get path to our assets
        sim_path = self.get_simulation_asset_path(sim)
        # set task to a blank slate
        sim.task = None
        # load assets first
        if dict_sim['assets']:
            # load the assets
            ac = AssetCollection()
            for dict_asset in dict_sim['assets']:
                if dict_asset['absolute_path'] is None:
                    if dict_asset['relative_path']:
                        dict_asset['absolute_path'] = os.path.join(sim_path, dict_asset['relative_path'], dict_asset['filename'])
                    else:
                        dict_asset['absolute_path'] = os.path.join(sim_path, dict_asset['filename'])
                asset = Asset(**dict_asset)
                asset.persisted = True
                asset.download_generator_hook = partial(file_contents_to_generator, asset.absolute_path)
                ac.add_asset(asset)
            sim.assets = ac
        # should we fully load the task?
        if load_task:
            if dict_sim['tags'] and 'task_type' in dict_sim['tags']:
                try:
                    sim.task = TaskFactory().create(dict_sim['tags']['task_type'], **dict_sim['task'])
                except Exception as e:
                    logger.exception(e)

            cli = self._detect_command_line_from_simulation(dict_sim)
            # if we could not find task, set it now, otherwise rebuild the cli
            if sim.task is None:
                sim.task = CommandTask(CommandLine.from_string(cli))
            else:
                sim.task.command = CommandLine.from_string(cli)
            # call task load options(load configs from files, etc)
            sim.task.reload_from_simulation(sim)
        else:
            cli = self._detect_command_line_from_simulation(dict_sim)
            sim.task = CommandTask(cli)

        # load assets
        return sim

    def _detect_command_line_from_simulation(self, dict_sim):
        if 'task' in dict_sim and 'command' in dict_sim['task']:
            return dict_sim['task']['command']
        return ''




