from dataclasses import dataclass
from typing import List, Any, Dict

from idmtools.entities import IPlatform
from idmtools.entities.iexperiment import TExperiment
from idmtools.entities.isimulation import TSimulationBatch, TSimulation


@dataclass
class SlurmPlatform(IPlatform):
    def create_experiment(self, experiment: TExperiment) -> None:
        pass

    def create_simulations(self, simulation_batch: TSimulationBatch) -> List[Any]:
        pass

    def run_simulations(self, experiment: TExperiment) -> None:
        pass

    def send_assets_for_experiment(self, experiment: TExperiment, **kwargs) -> None:
        pass

    def send_assets_for_simulation(self, simulation: TSimulation, **kwargs) -> None:
        pass

    def refresh_experiment_status(self, experiment: TExperiment) -> None:
        pass

    def restore_simulations(self, experiment: TExperiment) -> None:
        pass

    def get_assets_for_simulation(self, simulation: TSimulation, output_files: List[str]) -> Dict[str, bytearray]:
        pass

    def retrieve_experiment(self, experiment_id: 'uuid') -> TExperiment:
        pass