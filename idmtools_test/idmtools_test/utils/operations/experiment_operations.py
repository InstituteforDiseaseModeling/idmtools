import os
from dataclasses import field, dataclass
from logging import getLogger, DEBUG
from threading import Lock
from typing import List, Any, Type, Dict, Union, TYPE_CHECKING
from idmtools.core import EntityStatus, UnknownItemException
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform_ops.iplatform_experiment_operations import IPlatformExperimentOperations
if TYPE_CHECKING:  # pragma: no cover
    from idmtools_test.utils.test_platform import TestPlatform

logger = getLogger(__name__)
current_directory = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.abspath(os.path.join(current_directory, "..", "..", "data"))
EXPERIMENTS_LOCK = Lock()


@dataclass
class TestPlatformExperimentOperation(IPlatformExperimentOperations):
    platform: 'TestPlatform'
    platform_type: Type = Experiment
    experiments: Dict[str, Experiment] = field(default_factory=dict, compare=False, metadata={"pickle_ignore": True})

    def get(self, experiment_id: str, **kwargs) -> Experiment:
        e = self.experiments.get(experiment_id)
        if e is None:
            raise UnknownItemException(f"Cannot find the experiment with the ID of: {experiment_id}")
        e.platform = self.platform
        return e

    def platform_create(self, experiment: Experiment, **kwargs) -> Experiment:
        if logger.isEnabledFor(DEBUG):
            logger.debug('Creating Experiment')
        EXPERIMENTS_LOCK.acquire()
        self.experiments[experiment.uid] = experiment
        EXPERIMENTS_LOCK.release()
        self.platform._simulations._save_simulations_to_cache(experiment.uid, list(), overwrite=True)
        logger.debug(f"Created Experiment {experiment.uid}")
        return experiment

    def get_children(self, experiment: Experiment, **kwargs) -> List[Any]:
        return self.platform._simulations.simulations.get(experiment.uid)

    def get_parent(self, experiment: Any, **kwargs) -> Any:
        return None

    def platform_run_item(self, experiment: Experiment, **kwargs):
        self.platform._simulations.set_simulation_status(experiment.uid, EntityStatus.RUNNING)

    def send_assets(self, experiment: Any, **kwargs):
        pass

    def refresh_status(self, experiment: Experiment, **kwargs):
        if logger.isEnabledFor(DEBUG):
            logger.debug(f'Refreshing status for Experiment: {experiment.uid}')
        for simulation in self.platform._simulations.simulations.get(experiment.uid):
            for esim in experiment.simulations:
                if esim == simulation:
                    logger.debug(f'Setting {simulation.uid} Status to {simulation.status}')
                    esim.status = simulation.status
                    break

    def list_assets(self, experiment: Experiment, **kwargs) -> List[str]:
        pass
