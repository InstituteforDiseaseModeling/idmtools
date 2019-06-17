import os
import shelve
import uuid
import typing

import numpy as np

from idmtools.entities import IPlatform
from idmtools.services.experiments import ExperimentPersistService
from idmtools.services.simulations import SimulationPersistService

if typing.TYPE_CHECKING:
    from idmtools.core import TExperiment

current_directory = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.abspath(os.path.join(current_directory, "..", "data"))


class TestPlatform(IPlatform):
    """
    Test platform simulating a working platform to use in the test suites.
    """
    pickle_ignore_fields = ["experiments", "simulations"]

    def __init__(self):
        super().__init__()
        # Create the data path
        print(data_path)
        os.makedirs(data_path, exist_ok=True)
        self.experiments = ExperimentPersistService()
        self.simulations = SimulationPersistService()

    def restore_simulations(self, experiment: 'TExperiment') -> None:
        for sim in self.simulations[str(experiment.uid)]:
            s = experiment.simulation()
            s.uid = sim.uid
            s.status = sim.status
            s.tags = sim.tags
            experiment.simulations.append(s)

    def cleanup(self):
        ex = self.experiments._open_cache()
        ex.clear()
        ex.close(  )
        sm = self.simulations._open_cache()
        sm.clear()
        sm.close()

    def post_setstate(self):
        self.experiments = ExperimentPersistService()
        self.simulations = SimulationPersistService()

    def create_experiment(self, experiment: 'TExperiment') -> None:
        uid = uuid.uuid4()
        experiment.uid = uid
        self.experiments[str(uid)] = experiment

    def create_simulations(self, batch):
        simulations = []
        experiment_id = None
        for simulation in batch:
            experiment_id = simulation.experiment.uid
            simulation.uid = uuid.uuid4()
            simulations.append(simulation)
        self.simulations[str(experiment_id)] = simulations
        return [s.uid for s in simulations]

    def set_simulation_status(self, experiment_uid, status):
        self.set_simulation_prob_status(str(experiment_uid), {status: 1})

    def set_simulation_prob_status(self, experiment_uid, status):
        for simulation in self.simulations[str(experiment_uid)]:
            status = np.random.choice(
                a=list(status.keys()),
                p=list(status.values())
            )
            simulation.status = status
        self.simulations.sync()

    def run_simulations(self, experiment: 'TExperiment') -> None:
        from idmtools.core import EntityStatus
        self.set_simulation_status(str(experiment.uid), EntityStatus.RUNNING)

    def send_assets_for_experiment(self, experiment: 'TExperiment', **kwargs) -> None:
        pass

    def send_assets_for_simulation(self, simulation: 'TSimulation', **kwargs) -> None:
        pass

    def refresh_experiment_status(self, experiment: 'TExperiment') -> None:
        for simulation in self.simulations[str(experiment.uid)]:
            for esim in experiment.simulations:
                if esim == simulation:
                    esim.status = simulation.status
                    break
