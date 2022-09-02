import copy
import os
import shutil
from concurrent.futures._base import as_completed, Executor
from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Union, Type
from tqdm import tqdm
from idmtools.core import ItemType
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform import IPlatform
from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools.entities.platform_requirements import PlatformRequirements
from idmtools.registry.platform_specification import PlatformSpecification, get_platform_impl, \
    example_configuration_impl, get_platform_type_impl
from idmtools.registry.plugin_specification import get_description_impl
from idmtools_test.utils.execute_operations.experiment_operations import TestExecutePlatformExperimentOperation
from idmtools_test.utils.execute_operations.simulate_operations import TestExecutePlatformSimulationOperation

supported_types = [PlatformRequirements.SHELL, PlatformRequirements.NativeBinary, PlatformRequirements.PYTHON,
                   PlatformRequirements.WINDOWS if os.name == "nt" else PlatformRequirements.LINUX]


class PoolType(Enum):
    thread = ThreadPoolExecutor
    process = ProcessPoolExecutor


DEFAULT_OUTPUT_PATH = Path(os.getenv("IDMTOOLS_TEST_EXECUTE_PATH", Path().cwd().joinpath(".test_platform")))


def clear_execute_platform():
    for file in os.listdir(DEFAULT_OUTPUT_PATH):
        path = Path(DEFAULT_OUTPUT_PATH).joinpath(file)
        try:
            shutil.rmtree(path)
        except OSError:
            os.remove(path)


@dataclass(repr=False)
class TestExecutePlatform(IPlatform):
    _experiments: TestExecutePlatformExperimentOperation = field(
        default=None, compare=False, metadata={"pickle_ignore": True}, repr=False, init=False
    )
    _simulations: TestExecutePlatformSimulationOperation = field(default=None, compare=False, metadata={"pickle_ignore": True},
                                                                 repr=False, init=False)

    _platform_supports: List[PlatformRequirements] = field(default_factory=lambda: copy.deepcopy(supported_types),
                                                           repr=False, init=False)

    __test__ = False  # Hide from test discovery
    execute_directory: str = field(default=DEFAULT_OUTPUT_PATH)
    pool: Executor = field(default=None, compare=False, metadata={"pickle_ignore": True}, repr=False, init=False)
    pool_type: PoolType = field(default=PoolType.thread)
    queue: List = field(default_factory=list, compare=False, metadata={"pickle_ignore": True}, repr=False, init=False)
    workers: int = field(default=os.cpu_count()-1 if os.cpu_count() > 1 else 1)

    def __post_init__(self):
        self.init_interfaces()
        self.supported_types = {ItemType.EXPERIMENT, ItemType.SIMULATION}
        self.pool = self.pool_type.value(max_workers=self.workers)
        super().__post_init__()

    def init_interfaces(self):
        self._experiments = TestExecutePlatformExperimentOperation(self)
        self._simulations = TestExecutePlatformSimulationOperation(self)

    def post_setstate(self):
        self.init_interfaces()

    def run_simulations(self, experiment: Experiment) -> None:
        from idmtools.core import EntityStatus
        self._simulations.set_simulation_status(experiment.uid, EntityStatus.RUNNING)

    def cleanup(self):
        self._experiments.experiments = dict()
        self._simulations.simulations = dict()

    def wait_till_done(self, item: Union[Experiment, IWorkflowItem, Suite], timeout: int = 60 * 60 * 24,
                       refresh_interval: int = 5, progress=True):
        for future in as_completed(self.queue):
            result = future.result()
            for sim in self._simulations.simulations[result[0]]:
                if sim.id == result[1]:
                    sim.status = result[2]
                    break

    def wait_till_done_progress(self, item: Union[Experiment, IWorkflowItem, Suite], timeout: int = 60 * 60 * 24,
                                refresh_interval: int = 5):
        for future in tqdm(as_completed(self.queue), total=len(self.queue)):
            result = future.result()
            if isinstance(item, Experiment):
                for sim in item.simulations:
                    if sim.id == result[1]:
                        sim.status = result[2]
                        self._simulations.save_metadata(sim, update_data=dict(status=result[2]))
                        break
        del self.queue
        self.queue = []

    def __del__(self):
        self.pool.shutdown(False)


class TestExecutePlatformSpecification(PlatformSpecification):

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
        return TestExecutePlatform(**configuration)

    @example_configuration_impl
    def example_configuration(self):
        return ""

    @get_platform_type_impl
    def get_type(self) -> Type[TestExecutePlatform]:
        return TestExecutePlatform