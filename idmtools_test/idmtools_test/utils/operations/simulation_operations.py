import os
from dataclasses import dataclass, field
from logging import getLogger, DEBUG
from threading import Lock
from typing import List, Dict, Any, Type, TYPE_CHECKING
from uuid import uuid4
import numpy as np
from idmtools.assets import Asset
from idmtools.entities.iplatform_ops.iplatform_simulation_operations import IPlatformSimulationOperations
from idmtools.entities.simulation import Simulation
if TYPE_CHECKING:  # pragma: no cover
    from idmtools_test.utils.test_platform import TestPlatform
current_directory = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.abspath(os.path.join(current_directory, "..", "..", "data"))

logger = getLogger(__name__)
SIMULATION_LOCK = Lock()


@dataclass
class TestPlatformSimulationOperation(IPlatformSimulationOperations):
    platform: 'TestPlatform'

    def all_files(self, simulation: Simulation, **kwargs):
        pass

    platform_type: Type = Simulation
    simulations: dict = field(default_factory=dict, compare=False, metadata={"pickle_ignore": True})

    def get(self, simulation_id: str, **kwargs) -> Any:
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
        experiment_id = simulation.parent_id
        simulation.uid = str(uuid4())

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
                self.post_create(simulation)
                simulations.append(simulation)

        if experiment_id:
            self._save_simulations_to_cache(experiment_id, simulations)
        return simulations

    def get_parent(self, simulation: Any, **kwargs) -> Any:
        return self.platform._experiments.experiments.get(simulation.parent_id)

    def platform_run_item(self, simulation: Simulation, **kwargs):
        pass

    def send_assets(self, simulation: Any, **kwargs):
        pass

    def refresh_status(self, simulation: Simulation, **kwargs):
        pass

    def get_assets(self, simulation: Simulation, files: List[str], **kwargs) -> Dict[str, bytearray]:
        return {}

    def list_assets(self, simulation: Simulation, **kwargs) -> List[Asset]:
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
