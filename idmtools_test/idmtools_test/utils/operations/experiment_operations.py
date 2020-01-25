import os
from dataclasses import field, dataclass
from logging import getLogger, DEBUG
from typing import List, Any, Tuple, Type
from uuid import UUID, uuid4
import diskcache
from idmtools.core import EntityStatus, UnknownItemException
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform_ops.iplatform_experiment_operations import IPlatformExperimentOperations
from idmtools_test.utils.operations.simulation_operations import SIMULATION_LOCK

logger = getLogger(__name__)
current_directory = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.abspath(os.path.join(current_directory, "..", "..", "data"))


@dataclass
class TestPlaformExperimentOperation(IPlatformExperimentOperations):
    platform_type: Type = Experiment
    experiments: diskcache.Cache = field(default=None, compare=False, metadata={"pickle_ignore": True})

    def __post_init__(self):
        self.experiments = diskcache.Cache(os.path.join(data_path, 'experiments_test'))

    def get(self, experiment_id: UUID, **kwargs) -> Experiment:
        e = self.experiments.get(experiment_id)
        if e is None:
            raise UnknownItemException(f"Cannot find the experiment with the ID of: {experiment_id}")
        e.platform = self.platform
        return e

    def platform_create(self, experiment: Experiment, **kwargs) -> Tuple[Experiment, UUID]:
        if logger.isEnabledFor(DEBUG):
            logger.debug('Creating Experiment')
        uid = uuid4()
        experiment.uid = uid
        self.experiments.set(uid, experiment)
        self.platform._simulations._save_simulations_to_cache(uid, list(), overwrite=True)
        logger.debug(f"Created Experiment {experiment.uid}")
        return experiment, experiment.uid

    def get_children(self, experiment: Experiment, **kwargs) -> List[Any]:
        return self.platform._simulations.simulations.get(experiment.uid)

    def get_parent(self, experiment: Any, **kwargs) -> Any:
        return None

    def platform_run_item(self, experiment: Experiment):
        self.platform._simulations.set_simulation_status(experiment.uid, EntityStatus.RUNNING)

    def send_assets(self, experiment: Any):
        pass

    def refresh_status(self, experiment: Experiment):
        if logger.isEnabledFor(DEBUG):
            logger.debug(f'Refreshing status for Experiment: {experiment.uid}')
        for simulation in self.platform._simulations.simulations.get(experiment.uid):
            for esim in experiment.simulations:
                if esim == simulation:
                    logger.debug(f'Setting {simulation.uid} Status to {simulation.status}')
                    esim.status = simulation.status
                    break

    def list_assets(self, experiment: Experiment) -> List[str]:
        pass
