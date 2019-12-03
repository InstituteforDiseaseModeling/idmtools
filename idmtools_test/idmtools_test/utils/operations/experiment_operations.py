import os
from dataclasses import field, dataclass
from logging import getLogger
from typing import List, Any, Tuple, Type
from uuid import UUID, uuid4
import diskcache
from idmtools.core import EntityStatus, UnknownItemException
from idmtools.entities import IExperiment
from idmtools.entities.iplatform_metadata import IPlatformExperimentOperations

logger = getLogger(__name__)
current_directory = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.abspath(os.path.join(current_directory, "..", "..", "data"))

@dataclass
class TestPlaformExperimentOperation(IPlatformExperimentOperations):
    platform_type: Type = IExperiment
    experiments: diskcache.Cache = field(default=None, compare=False, metadata={"pickle_ignore": True})

    def __post_init__(self):
        self.experiments = diskcache.Cache(os.path.join(data_path, 'experiments_test'))

    def get(self, experiment_id: UUID, **kwargs) -> IExperiment:
        e = self.experiments.get(experiment_id)
        if e is None:
            raise UnknownItemException(f"Cannot find the experiment with the ID of: {experiment_id}")
        e.platform = self.platform
        return e

    def create(self, experiment: IExperiment, **kwargs) -> Tuple[IExperiment, UUID]:
        if not self.platform.is_supported_experiment(experiment):
            raise ValueError("The specified experiment is not supported on this platform")
        uid = uuid4()
        experiment.uid = uid
        self.experiments.set(uid, experiment)
        lock = diskcache.Lock(self.platform._simulations.simulations, 'simulations-lock')
        with lock:
            self.platform._simulations.simulations.set(uid, list())
        logger.debug(f"Created Experiment {experiment.uid}")
        return experiment, experiment.uid

    def get_children(self, experiment: IExperiment, **kwargs) -> List[Any]:
        return self.platform._simulations.simulations.get(experiment.uid)

    def get_parent(self, experiment: Any, **kwargs) -> Any:
        return None

    def run_item(self, experiment: IExperiment):
        self.platform._simulations.set_simulation_status(experiment.uid, EntityStatus.RUNNING)

    def send_assets(self, experiment: Any):
        pass

    def refresh_status(self, experiment: IExperiment):
        for simulation in self.platform._simulations.simulations.get(experiment.uid):
            for esim in experiment.simulations:
                if esim == simulation:
                    esim.status = simulation.status
                    break

    def list_assets(self, experiment: IExperiment) -> List[str]:
        pass
