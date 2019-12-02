from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Type
from uuid import UUID, uuid4

import diskcache
from pandas.tests.extension.numpy_.test_numpy_nested import np

from idmtools.entities import ISimulation
from idmtools.entities.iplatform_metadata import IPlatformSimulationOperations


@dataclass
class TestPlaformSimulationOperation(IPlatformSimulationOperations):
    platform_type: Type = ISimulation
    simulations: diskcache.Cache = field(default=None, compare=False, metadata={"pickle_ignore": True})

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

    def create(self, simulation: ISimulation, **kwargs) -> Tuple[Any, UUID]:
        experiment_id = simulation.parent_id
        simulation.uid = uuid4()

        lock = diskcache.Lock(self.simulations, 'simulations-lock')
        with lock:
            existing_simulations = self.simulations.pop(experiment_id)
            self.simulations[experiment_id] = existing_simulations + simulation
        return simulation, simulation.uid

    def batch_create(self, sims: List[ISimulation], **kwargs) -> List[Tuple[Any, UUID]]:
        simulations = []
        for simulation in sims:
            experiment_id = simulation.parent_id
            simulation.uid = uuid4()
            simulations.append(simulation)

        lock = diskcache.Lock(self.simulations, 'simulations-lock')
        with lock:
            existing_simulations = self.simulations.pop(experiment_id)
            self.simulations[experiment_id] = existing_simulations + simulations
        return [(s, s.uid) for s in simulations]

    def get_parent(self, simulation: Any, **kwargs) -> Any:
        return self.platform._experiments.experiments.get(simulation.parent_id)

    def run_item(self, simulation: ISimulation):
        pass

    def send_assets(self, simulation: Any):
        pass

    def refresh_status(self, simulation: ISimulation):
        pass

    def get_assets(self, simulation: ISimulation, files: List[str], **kwargs) -> Dict[str, bytearray]:
        return {}

    def list_assets(self, simulation: ISimulation) -> List[str]:
        pass

    def set_simulation_status(self, experiment_uid, status):
        self.set_simulation_prob_status(experiment_uid, {status: 1})

    def set_simulation_prob_status(self, experiment_uid, status):
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