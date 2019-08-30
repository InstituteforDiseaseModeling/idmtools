import os
import shutil
import uuid
import typing
from dataclasses import dataclass, field

import diskcache
import numpy as np
from typing import Type

from idmtools.registry.PlatformSpecification import example_configuration_impl, get_platform_impl, \
    get_platform_type_impl, PlatformSpecification
from idmtools.registry.PluginSpecification import get_description_impl


from idmtools.entities import IPlatform



if typing.TYPE_CHECKING:
    from idmtools.core import TExperiment

current_directory = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.abspath(os.path.join(current_directory, "..", "data"))


@dataclass(repr=False)
class TestPlatform(IPlatform):
    """
    Test platform simulating a working platform to use in the test suites.
    """

    __test__ = False  # Hide from test discovery

    experiments: 'diskcache.Cache' = field(default=None, compare=False, metadata={"pickle_ignore": True})
    simulations: 'diskcache.Cache' = field(default=None, compare=False, metadata={"pickle_ignore": True})

    def __del__(self):
        # Close and delete the cache when finished
        if self.experiments:
            self.experiments.close()
        if self.simulations:
            self.simulations.close()
        if os.path.exists(data_path):
            try:
                shutil.rmtree(data_path)
            except OSError:
                pass

    def __post_init__(self):
        super().__post_init__()
        os.makedirs(data_path, exist_ok=True)
        self.initialize_test_cache()

    def initialize_test_cache(self):
        """
        Create a cache experiments/simulations that will only exist during test
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
            new_status = np.random.choice(
                a=list(status.keys()),
                p=list(status.values())
            )
            simulation.status = new_status
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

    def get_assets_for_simulation(self, simulation, output_files):
        pass

    def retrieve_experiment(self, experiment_id: 'uuid') -> 'TExperiment':
        if not experiment_id in self.experiments:
            return None
        return self.experiments[experiment_id]


TEST_PLATFORM_EXAMPLE_CONFIG = """
[LOCAL]
redis_image=redis:5.0.4-alpine
redis_port=6379
runtime=nvidia
workers_image: str = 'idm-docker-staging.packages.idmod.org:latest'
workers_ui_port: int = 5000
"""


class TestPlatformSpecification(PlatformSpecification):

    @get_description_impl
    def get_description(self) -> str:
        return "Provides access to the Test Platform to IDM Tools"

    @get_platform_impl
    def get(self, configuration: dict) -> IPlatform:
        """
        Build our test platform from the passed in configuration object

        We do our import of platform here to avoid any weir
        Args:
            configuration:

        Returns:

        """
        return TestPlatform(**configuration)

    @example_configuration_impl
    def example_configuration(self):
        return TEST_PLATFORM_EXAMPLE_CONFIG

    @get_platform_type_impl
    def get_type(self) -> Type[TestPlatform]:
        return TestPlatform
