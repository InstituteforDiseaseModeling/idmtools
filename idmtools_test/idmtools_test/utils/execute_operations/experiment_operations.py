import json
import os
import shutil
from dataclasses import field, dataclass
from logging import getLogger, DEBUG
from threading import Lock
from typing import Any, List, Type, Dict, Union, TYPE_CHECKING
from uuid import UUID, uuid4
from idmtools.core import UnknownItemException, EntityStatus
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform_ops.iplatform_experiment_operations import IPlatformExperimentOperations
from idmtools.utils.json import IDMJSONEncoder

if TYPE_CHECKING:
    from idmtools_test.utils.test_execute_platform import TestExecutePlatform

logger = getLogger(__name__)
current_directory = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.abspath(os.path.join(current_directory, "..", "..", "data"))
EXPERIMENTS_LOCK = Lock()


@dataclass
class TestExecutePlatformExperimentOperation(IPlatformExperimentOperations):
    platform: 'TestExecutePlatform'
    platform_type: Type = field(default=Experiment)
    experiments: Dict[str, Experiment] = field(default_factory=dict, compare=False, metadata={"pickle_ignore": True})

    def get(self, experiment_id: Union[str, UUID], **kwargs) -> Any:
        e = self.experiments.get(experiment_id if isinstance(experiment_id, UUID) else UUID(experiment_id))
        if e is None:
            raise UnknownItemException(f"Cannot find the experiment with the ID of: {experiment_id}")
        e.platform = self.platform
        return e

    def platform_create(self, experiment: Experiment, **kwargs) -> Any:
        if logger.isEnabledFor(DEBUG):
            logger.debug('Creating Experiment')
        uid = uuid4()
        experiment.uid = uid
        EXPERIMENTS_LOCK.acquire()
        self.experiments[uid] = experiment
        EXPERIMENTS_LOCK.release()
        self.platform._simulations._save_simulations_to_cache(uid, list(), overwrite=True)
        logger.debug(f"Created Experiment {experiment.uid}")
        self.send_assets(experiment, **kwargs)
        return experiment

    def get_children(self, experiment: Any, **kwargs) -> List[Any]:
        return self.platform._simulations.simulations.get(experiment.uid)

    def get_parent(self, experiment: Any, **kwargs) -> Experiment:
        pass

    def platform_run_item(self, experiment: Experiment, **kwargs):
        exp_path = os.path.join(self.platform.execute_directory, str(experiment.uid))
        path = os.path.join(exp_path, "experiment.json")
        os.makedirs(exp_path, exist_ok=True)
        with open(path, 'w') as out:
            out.write(json.dumps(experiment.to_dict(), cls=IDMJSONEncoder))
        for sim in experiment.simulations:
            self.platform._simulations.run_item(sim)
        self.platform._simulations.set_simulation_status(experiment.uid, EntityStatus.RUNNING)

    def send_assets(self, experiment: Experiment, **kwargs):
        path = os.path.join(self.platform.execute_directory, str(experiment.uid), "Assets")
        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Creating {path}")
        os.makedirs(path, exist_ok=True)
        for asset in experiment.assets:
            remote_path = os.path.join(path, asset.relative_path) if asset.relative_path else path
            remote_path = os.path.join(remote_path, asset.filename)
            if asset.absolute_path:
                if logger.isEnabledFor(DEBUG):
                    logger.debug(f"Copying {asset.absolute_path} to {remote_path}")
                shutil.copy(asset.absolute_path, remote_path)
            else:
                if logger.isEnabledFor(DEBUG):
                    logger.debug(f"Writing {asset.absolute_path} to {remote_path}")
                with open(remote_path, 'wb') as out:
                    out.write(asset.content)

    def refresh_status(self, experiment: Experiment, **kwargs):
        if logger.isEnabledFor(DEBUG):
            logger.debug(f'Refreshing status for Experiment: {experiment.uid}')
        for simulation in self.platform._simulations.simulations.get(experiment.uid):
            for esim in experiment.simulations:
                if esim == simulation:
                    logger.debug(f'Setting {simulation.uid} Status to {simulation.status}')
                    esim.status = simulation.status
                    break