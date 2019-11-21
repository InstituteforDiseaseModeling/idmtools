import os
import typing
from dataclasses import dataclass, field
from logging import getLogger
from typing import Dict, List, Type
from uuid import UUID, uuid4

import diskcache
import numpy as np

from idmtools.core import EntityStatus, ItemType
from idmtools.core.interfaces.iitem import TItem
from idmtools.entities import IPlatform
from idmtools.entities.experiment import TExperiment
from idmtools.entities.simulation import TSimulation
from idmtools.registry.platform_specification import example_configuration_impl, get_platform_impl, \
    get_platform_type_impl, PlatformSpecification
from idmtools.registry.plugin_specification import get_description_impl

current_directory = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.abspath(os.path.join(current_directory, "..", "data"))

logger = getLogger(__name__)


@dataclass(repr=False)
class TestPlatform(IPlatform):
    """
    Test platform simulating a working platform to use in the test suites.
    """

    def supported_experiment_types(self) -> List[typing.Type]:
        PlatformRequirements
        os_ex = IWindowsExperiment if os.name == "nt" else ILinuxExperiment
        return [IExperiment, os_ex]

    def unsupported_experiment_types(self) -> List[typing.Type]:
        os_ex = IWindowsExperiment if os.name != "nt" else ILinuxExperiment
        return [IGPUExperiment, IDockerExperiment, os_ex]

    __test__ = False  # Hide from test discovery

    experiments: 'diskcache.Cache' = field(default=None, compare=False, metadata={"pickle_ignore": True})
    simulations: 'diskcache.Cache' = field(default=None, compare=False, metadata={"pickle_ignore": True})

    def __post_init__(self):
        os.makedirs(data_path, exist_ok=True)
        self.initialize_test_cache()
        self.supported_types = {ItemType.EXPERIMENT, ItemType.SIMULATION}
        super().__post_init__()

    def initialize_test_cache(self):
        """
        Create a cache experiments/simulations that will only exist during test
        """
        self.experiments = diskcache.Cache(os.path.join(data_path, 'experiments_test'))
        self.simulations = diskcache.Cache(os.path.join(data_path, 'simulations_test'))

    def cleanup(self):
        for cache in [self.experiments, self.simulations]:
            cache.clear()
            cache.close()

    def post_setstate(self):
        self.initialize_test_cache()

    def _create_batch(self, batch: 'TEntityList', item_type: 'ItemType') -> 'List[UUID]':  # noqa: F821
        if item_type == ItemType.SIMULATION:
            return self._create_simulations(simulation_batch=batch)

        if item_type == ItemType.EXPERIMENT:
            return [self._create_experiment(experiment=item) for item in batch]

    def get_platform_item(self, item_id, item_type, **kwargs):
        if item_type == ItemType.SIMULATION:
            obj = None
            for eid in self.simulations:
                sims = self.simulations.get(eid)
                if sims:
                    for sim in self.simulations.get(eid):
                        if sim.uid == item_id:
                            obj = sim
                            break
                if obj:
                    break
        elif item_type == ItemType.EXPERIMENT:
            obj = self.experiments.get(item_id)

        if not obj:
            logger.warning(f"Could not find object with id: {item_id}")
            return

        obj.platform = self
        return obj

    def get_children_for_platform_item(self, platform_item, raw, **kwargs):
        if platform_item.item_type == ItemType.EXPERIMENT:
            return self.simulations.get(platform_item.uid)

    def get_parent_for_platform_item(self, platform_item, raw, **kwargs):
        if platform_item.item_type == ItemType.SIMULATION:
            return self.experiments.get(platform_item.parent_id)

    def _create_experiment(self, experiment: 'TExperiment') -> UUID:
        if not self.is_supported_experiment(experiment):
            raise ValueError("The specified experiment is not supported on this platform")
        uid = uuid4()
        experiment.uid = uid
        self.experiments.set(uid, experiment)
        lock = diskcache.Lock(self.simulations, 'simulations-lock')
        with lock:
            self.simulations.set(uid, list())
        logger.debug(f"Created Experiment {experiment.uid}")
        return experiment.uid

    def _create_simulations(self, simulation_batch):

        simulations = []
        for simulation in simulation_batch:
            experiment_id = simulation.parent_id
            simulation.uid = uuid4()
            simulations.append(simulation)

        lock = diskcache.Lock(self.simulations, 'simulations-lock')
        with lock:
            existing_simulations = self.simulations.pop(experiment_id)
            self.simulations[experiment_id] = existing_simulations + simulations
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

    def set_simulation_num_status(self, experiment_uid, status, number):
        simulations = self.simulations.get(experiment_uid)
        for simulation in simulations:
            simulation.status = status
            self.simulations.set(experiment_uid, simulations)
            number -= 1
            if number <= 0:
                return

    def run_simulations(self, experiment: TExperiment) -> None:
        from idmtools.core import EntityStatus
        self.set_simulation_status(experiment.uid, EntityStatus.RUNNING)

    def send_assets_for_experiment(self, experiment: TExperiment, **kwargs) -> None:
        pass

    def send_assets_for_simulation(self, simulation: TSimulation, **kwargs) -> None:
        pass

    def refresh_status(self, item) -> None:
        for simulation in self.simulations.get(item.uid):
            for esim in item.simulations():
                if esim == simulation:
                    esim.status = simulation.status
                    break

    def run_items(self, items: 'TItem'):
        for item in items:
            if item.item_type == ItemType.EXPERIMENT:
                self.set_simulation_status(item.uid, EntityStatus.RUNNING)

    def send_assets(self, item: 'TItem', **kwargs):
        pass

    def get_files(self, item: 'TItem', files: 'List[str]') -> Dict[str, bytearray]:
        pass


TEST_PLATFORM_EXAMPLE_CONFIG = """
[Test]

"""


class TestPlatformSpecification(PlatformSpecification):

    @get_description_impl
    def get_description(self) -> str:
        return "Provides access to the Test Platform to IDM Tools"

    @get_platform_impl
    def get(self, **configuration) -> IPlatform:
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
