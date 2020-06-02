import json
import os
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from logging import getLogger, DEBUG
from threading import Lock
from typing import List, Dict, Any, Type, TYPE_CHECKING, TextIO
from uuid import UUID, uuid4
import numpy as np

from idmtools.core import EntityStatus
from idmtools.entities.iplatform_ops.iplatform_simulation_operations import IPlatformSimulationOperations
from idmtools.entities.simulation import Simulation
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

            # Run our task
            p = subprocess.Popen(
                shlex.split(cmd),
                cwd=simulation_path,
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
        exp_path = os.path.join(self.platform.execute_directory, str(simulation.parent.uid))
        sim_path = os.path.join(exp_path, str(simulation.id))
        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Creating {exp_path}")
        os.makedirs(sim_path, exist_ok=True)
        for asset in simulation.assets:
            remote_path = os.path.join(sim_path, asset.relative_path) if asset.relative_path else sim_path
            remote_path = os.path.join(remote_path, asset.filename)
            if asset.absolute_path:
                if logger.isEnabledFor(DEBUG):
                    logger.debug(f"Copying {asset.absolute_path} to {remote_path}")
                shutil.copy(asset.absolute_path, remote_path)
            else:
                if logger.isEnabledFor(DEBUG):
                    logger.debug(f"Writing {asset.absolute_path} to {remote_path}")
                with open(os.path.join(remote_path), 'wb') as out:
                    out.write(asset.content.encode())

        import win32file
        exp_path = os.path.join(exp_path, "Assets")

        for asset in simulation.parent.assets:
            remote_path = os.path.join(exp_path, asset.relative_path) if asset.relative_path else exp_path
            sim_assets = os.path.join(sim_path, "Assets")
            src_path = os.path.join(remote_path, asset.filename)
            dest_path = os.path.join(sim_assets, asset.filename)
            os.makedirs(sim_assets, exist_ok=True)
            if sys.platform in ['win32']:
                try:
                    win32file.CreateSymbolicLink(src_path, dest_path, 1)
                except Exception as e:
                    shutil.copy(src_path, dest_path)
            else:
                os.symlink(src_path, dest_path)


    def refresh_status(self, simulation: Simulation, **kwargs):
        pass

    def get_assets(self, simulation: Simulation, files: List[str], **kwargs) -> Dict[str, bytearray]:
        return {}

    def list_assets(self, simulation: Simulation, **kwargs) -> List[str]:
        pass

    def set_simulation_status(self, experiment_uid, status):
        self.set_simulation_prob_status(experiment_uid, {status: 1})

    def set_simulation_prob_status(self, experiment_uid, status):
        if logger.isEnabledFor(DEBUG):
            logger.debug(f'Setting status for sim s on exp {experiment_uid} to {status}')
        simulations = self.simulations.get(experiment_uid)
        for simulation in simulations:
            new_status = np.random.choice(
                a=list(status.keys()),
                p=list(status.values())
            )
            simulation.status = new_status
        self._save_simulations_to_cache(experiment_uid, simulations, True)

    def set_simulation_num_status(self, experiment_uid, status, number):
        simulations = self.simulations.get(experiment_uid)
        for simulation in simulations:
            simulation.status = status
            number -= 1
            if number <= 0:
                break
        self._save_simulations_to_cache(experiment_uid, simulations, True)
