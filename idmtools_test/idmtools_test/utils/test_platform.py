import os
import shutil
import uuid
import typing
from dataclasses import dataclass, field

import diskcache
import numpy as np
from typing import Type

from idmtools.core import UnknownItemException
from idmtools.registry.platform_specification import example_configuration_impl, get_platform_impl, \
    get_platform_type_impl, PlatformSpecification
from idmtools.registry.plugin_specification import get_description_impl

from idmtools.entities import IPlatform
from idmtools.entities import IExperiment
from idmtools.entities import ISimulation

if typing.TYPE_CHECKING:
    from idmtools.entities.ianalyzer import TAnalyzerList
    from idmtools.entities.iexperiment import TExperiment
    from idmtools.entities.iitem import TItem, TItemList

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
        self.experiments.close()
        self.simulations.close()
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

    def get_children(self, item: 'TItem') -> 'TItemList':
        children = None
        successful = False
        if not successful:
            children = self._restore_simulations(experiment=item)
            successful = True
        if not successful:
            raise UnknownItemException(f'Unable to retrieve children for unknown item '
                                            f'id: {item.uid} of type: {type(item)}')
        for child in children:
            child.platform = self
        return children

    def _restore_simulations(self, experiment: 'TExperiment') -> None:

        simulations = self.simulations.get(experiment.uid)
        for sim in simulations:
            s = experiment.simulation()
            s.uid = sim.uid
            s.status = sim.status
            s.tags = sim.tags
            s.parent_id = experiment.uid
            s.platform = self
        return simulations

    def cleanup(self):
        for cache in [self.experiments, self.simulations]:
            cache.clear()
            cache.close()

    def post_setstate(self):
        self.initialize_test_cache()

    def create_items(self, items: 'TItemList') -> 'List[uuid]':
        # TODO: add ability to create suites
        types = list({type(item) for item in items})
        if len(types) != 1:
            raise Exception('create_items only works with items of a single type at a time.')
        sample_item = items[0]
        if isinstance(sample_item, ISimulation):
            ids = self._create_simulations(simulation_batch=items)
        elif isinstance(sample_item, IExperiment):
            ids = [self._create_experiment(experiment=item) for item in items]
        else:
            raise Exception(f'Unable to create items of type: {type(sample_item)} '
                            f'for platform: {self.__class__.__name__}')
        for item in items:
            item.platform = self
        return ids

    def _create_experiment(self, experiment: 'TExperiment') -> uuid.UUID:
        uid = uuid.uuid4()
        experiment.uid = uid
        self.experiments.set(uid, experiment)
        lock = diskcache.Lock(self.simulations, 'simulations-lock')
        with lock:
            self.simulations.set(uid, list())
        return experiment.uid

    def _create_simulations(self, simulation_batch):
        simulations = []
        experiment_id = None
        for simulation in simulation_batch:
            experiment_id = experiment_id or simulation.parent.uid
            simulation.uid = uuid.uuid4()
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

    def run_simulations(self, experiment: 'TExperiment') -> None:
        from idmtools.core import EntityStatus
        self.set_simulation_status(experiment.uid, EntityStatus.RUNNING)

    def send_assets_for_experiment(self, experiment: 'TExperiment', **kwargs) -> None:
        pass

    def send_assets_for_simulation(self, simulation: 'TSimulation', **kwargs) -> None:
        pass

    def refresh_experiment_status(self, experiment: 'TExperiment') -> None:
        for simulation in self.simulations.get(experiment.uid):
            for esim in experiment.children():
                if esim == simulation:
                    esim.status = simulation.status
                    break

    def get_assets_for_simulation(self, simulation, output_files):
        pass

    def get_item(self, id: 'uuid'):
        successful = False
        if not successful:
            try:
                item = self._retrieve_experiment(experiment_id=id)
                successful = True
            except:
                pass
        if not successful:
            raise UnknownItemException(f'Unable to load item id: {id} from platform: {self.__class__.__name__}')

        item.platform = self
        return item

    def _retrieve_experiment(self, experiment_id: 'uuid') -> 'TExperiment':
        if not experiment_id in self.experiments:
            raise Exception('No experiment id found: %s' % experiment_id)
        return self.experiments[experiment_id]

    # not currently used, but if we ever need to retrieve a single simulation instead of an experiment...
    def _retrieve_simulation(self, simulation_id: 'uuid') -> 'TSimulation':
        found = False
        for experiment_id in self.simulations.iterkeys():
            simulations = self.simulations[experiment_id]
            matches = [sim for sim in simulations if sim.uid == simulation_id]
            if len(matches) == 1:
                simulation = matches[0]
                found = experiment_id
                break
            elif len(matches) > 1:
                raise Exception('Duplicate simulations found for id: %s' % simulation_id)
        if not found:
            raise Exception('Simulation not found: %s' % simulation_id)
        simulation.experiment_id = experiment_id
        return simulation

    #
    # do we need any details for these methods for TestPlatform???
    #

    def get_parent(self, item: 'TItem') -> 'TItem':
        parent = None
        successful = False
        if not successful:
            try:
                parent = self._retrieve_experiment(experiment_id=item.parent_id)
                successful = True
            except:
                pass
        if not successful:
            raise UnknownItemException(f'Unable to retrieve parent for unknown item '
                                            f'id: {item.uid} of type: {type(item)}')
        parent.platform = self
        return parent

    def initialize_for_analysis(self, items: 'TItemList', analyzers: 'TAnalyzerList'):
        pass

    def run_items(self, items: 'TItem'):
        pass

    def send_assets(self, item: 'TItem', **kwargs):
        pass

    def refresh_status(self, item):
        pass

    def get_files(self, item: 'TItem', files: 'List[str]') -> 'Dict[str, bytearray]':
        pass

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
