import os
from dataclasses import dataclass, field
from logging import getLogger, DEBUG
from typing import List, Dict, Any, Tuple, Type
from uuid import UUID, uuid4
import diskcache
from pandas.tests.extension.numpy_.test_numpy_nested import np
from idmtools.entities.iplatform_ops.iplatform_simulation_operations import IPlatformSimulationOperations
from idmtools.entities.simulation import Simulation

current_directory = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.abspath(os.path.join(current_directory, "..", "..", "data"))

logger = getLogger(__name__)


@dataclass
class TestPlaformSimulationOperation(IPlatformSimulationOperations):
    platform_type: Type = Simulation
    simulations: diskcache.Cache = field(default=None, compare=False, metadata={"pickle_ignore": True})

    def __post_init__(self):
        self.simulations = diskcache.Cache(os.path.join(data_path, 'simulations_test'))

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

    def platform_create(self, simulation: Simulation, **kwargs) -> Tuple[Any, UUID]:
        experiment_id = simulation.parent_id
        simulation.uid = uuid4()

        self._save_simulations_to_cache(experiment_id, [simulation])
        return simulation, simulation.uid

    def _save_simulations_to_cache(self, experiment_id, simulations: List[Simulation]):
        if logger.isEnabledFor(DEBUG):
            logger.debug(f'Saving {len(simulations)} to Experiment {experiment_id}')
        lock = diskcache.Lock(self.simulations, 'simulations-lock')
        with lock:
            existing_simulations = self.simulations.pop(experiment_id)
            self.simulations[experiment_id] = existing_simulations + simulations

    def batch_create(self, sims: List[Simulation], **kwargs) -> List[Tuple[Any, UUID]]:
        simulations = []
        experiment_id = None
        for simulation in sims:
            self.pre_create(simulation)
            experiment_id = simulation.parent_id
            simulation.uid = uuid4()
            self.post_create(simulation)
            simulations.append(simulation)

        if experiment_id:
            self._save_simulations_to_cache(experiment_id, simulations)
        return [(s, s.uid) for s in simulations]

    def get_parent(self, simulation: Any, **kwargs) -> Any:
        return self.platform._experiments.experiments.get(simulation.parent_id)

    def platform_run_item(self, simulation: Simulation):
        pass

    def send_assets(self, simulation: Any):
        pass

    def refresh_status(self, simulation: Simulation):
        pass

    def get_assets(self, simulation: Simulation, files: List[str], **kwargs) -> Dict[str, bytearray]:
        return {}

    def list_assets(self, simulation: Simulation) -> List[str]:
        pass

    def set_simulation_status(self, experiment_uid, status):
        self.set_simulation_prob_status(experiment_uid, {status: 1})

    def set_simulation_prob_status(self, experiment_uid, status):
        if logger.isEnabledFor(DEBUG):
            logger.debug(f'Setting status for sims on exp {experiment_uid} to {status}')
        simulations = self.simulations.get(experiment_uid)
        for simulation in simulations:
            new_status = np.random.choice(
                a=list(status.keys()),
                p=list(status.values())
            )
            simulation.status = new_status
        self.simulations.set(experiment_uid, simulations)

    def set_simulation_num_status(self, experiment_uid, status, number):
        simulations = self.simulations.get(experiment_uid)
        for simulation in simulations:
            simulation.status = status
            self.simulations.set(experiment_uid, simulations)
            number -= 1
            if number <= 0:
                return
