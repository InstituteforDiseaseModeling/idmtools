import os
import uuid
import typing
import diskcache
import numpy as np
from idmtools.entities import IPlatform

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
        self.experiments: diskcache.Cache = None
        self.simulations: diskcache.Cache = None
        self.initialize_test_cache()

    def initialize_test_cache(self):
        """
        Create a cache experiments/simulations that will only exist during test
        :return:
        """
        self.experiments = diskcache.Cache(os.path.join(data_path, 'experiments_test'))
        self.simulations = diskcache.Cache(os.path.join(data_path, 'simulations_test'))

    def restore_simulations(self, experiment: 'TExperiment') -> None:
        for sim in self.simulations.get(experiment.uid):
            s = experiment.simulation()
            s.uid = sim.uid
            s.status = sim.status
            s.tags = sim.tags
            experiment.simulations.append(s)

    def cleanup(self):
        for cache in [self.experiments, self.simulations]:
            cache.clear()
            cache.close()

    def post_setstate(self):
        self.initialize_test_cache()

    def create_experiment(self, experiment: 'TExperiment') -> None:
        uid = uuid.uuid4()
        experiment.uid = uid
        self.experiments.set(uid, experiment)

    def create_simulations(self, batch):
        simulations = []
        experiment_id = None
        for simulation in batch:
            experiment_id = simulation.experiment.uid
            simulation.uid = uuid.uuid4()
            simulations.append(simulation)

        self.simulations.set(experiment_id, simulations)
        return [s.uid for s in simulations]

    def set_simulation_status(self, experiment_uid, status):
        self.set_simulation_prob_status(experiment_uid, {status: 1})

    def set_simulation_prob_status(self, experiment_uid, status):
        simulations = self.simulations.get(experiment_uid)
        for simulation in simulations:
            status = np.random.choice(
                a=list(status.keys()),
                p=list(status.values())
            )
            simulation.status = status
        self.simulations.set(experiment_uid, simulations)

    def run_simulations(self, experiment: 'TExperiment') -> None:
        from idmtools.core import EntityStatus
        self.set_simulation_status(experiment.uid, EntityStatus.RUNNING)

    def send_assets_for_experiment(self, experiment: 'TExperiment', **kwargs) -> None:
        pass

    def send_assets_for_simulation(self, simulation: 'TSimulation', **kwargs) -> None:
        pass

    def refresh_experiment_status(self, experiment: 'TExperiment') -> None:
        for simulation in self.simulations.get(experiment.uid):
            for esim in experiment.simulations:
                if esim == simulation:
                    esim.status = simulation.status
                    break
