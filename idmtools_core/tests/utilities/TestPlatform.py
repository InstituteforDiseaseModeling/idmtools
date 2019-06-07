import os
import shelve
import uuid

import numpy as np

from idmtools.entities import IPlatform

current_directory = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.abspath(os.path.join(current_directory, "..", "data"))


class TestPlatform(IPlatform):
    """
    Test platform simulating a working platform to use in the test suites.
    """
    pickle_ignore_fields = ["shelf"]

    def __init__(self):
        super().__init__()
        # Create the data path
        print(data_path)
        os.makedirs(data_path, exist_ok=True)
        self.shelf = shelve.open(os.path.join(data_path, "shelve"), writeback=True)

    def cleanup(self):
        self.shelf.clear()

    def __del__(self):
        self.shelf.close()

    def _post_setstate(self):
        self.shelf = shelve.open(os.path.join(data_path, "shelve"), writeback=True)

    def create_experiment(self, experiment: 'TExperiment') -> None:
        uid = uuid.uuid4()
        experiment.uid = uid
        self.shelf[str(uid)] = experiment

    def create_simulations(self, experiment: 'TExperiment') -> None:
        for simulation in experiment.simulations:
            simulation.uid = uuid.uuid4()
        self.shelf[str(experiment.uid)] = experiment

    def set_simulation_status(self, experiment_uid, status):
        self.set_simulation_prob_status(experiment_uid, {status: 1})

    def set_simulation_prob_status(self, experiment_uid, status):
        for simulation in self.shelf[str(experiment_uid)].simulations:
            status = np.random.choice(
                a=list(status.keys()),
                p=list(status.values())
            )
            simulation.status = status

    def run_simulations(self, experiment: 'TExperiment') -> None:
        pass

    def send_assets_for_experiment(self, experiment: 'TExperiment', **kwargs) -> None:
        pass

    def send_assets_for_simulation(self, simulation: 'TSimulation', **kwargs) -> None:
        pass

    def refresh_experiment_status(self, experiment: 'TExperiment') -> None:
        pass
