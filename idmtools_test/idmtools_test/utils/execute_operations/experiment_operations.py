import hashlib
import io
import json
import os
import shutil
from dataclasses import field, dataclass
from functools import partial
from logging import getLogger, DEBUG
from threading import Lock
from typing import Any, List, Type, Dict, Union, TYPE_CHECKING, Optional
from idmtools.assets import Asset, AssetCollection
from idmtools.core import EntityStatus, ItemType
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform_ops.iplatform_experiment_operations import IPlatformExperimentOperations
from idmtools.utils.file import file_contents_to_generator
from idmtools.utils.json import IDMJSONEncoder

if TYPE_CHECKING:  # pragma: no cover
    from idmtools_test.utils.test_execute_platform import TestExecutePlatform

logger = getLogger(__name__)
current_directory = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.abspath(os.path.join(current_directory, "..", "..", "data"))
EXPERIMENTS_LOCK = Lock()


class ExperimentDict(dict):
    pass


@dataclass
class TestExecutePlatformExperimentOperation(IPlatformExperimentOperations):
    platform: 'TestExecutePlatform'
    platform_type: Type = field(default=ExperimentDict)
    experiments: Dict[str, Experiment] = field(default_factory=dict, compare=False, metadata={"pickle_ignore": True})

    def get(self, experiment_id: Union[str], **kwargs) -> Any:
        exp_path = self.get_experiment_path(experiment_id)
        path = os.path.join(exp_path, "experiment.json")
        if not os.path.exists(path):
            logger.error(f"Cannot find experiment with id {experiment_id}")
            raise FileNotFoundError(f"Cannot find experiment with id {experiment_id}")

        logger.info(f"Loading experiment metadata from {path}")
        with open(path, 'r') as metadata_in:
            metadata = json.load(metadata_in)
            return ExperimentDict(metadata)

    def platform_create(self, experiment: Experiment, **kwargs) -> Any:
        if logger.isEnabledFor(DEBUG):
            logger.debug('Creating Experiment')
        EXPERIMENTS_LOCK.acquire()
        self.experiments[experiment.uid] = experiment
        EXPERIMENTS_LOCK.release()
        logger.debug(f"Created Experiment {experiment.uid}")
        self.send_assets(experiment, **kwargs)
        return experiment

    def get_children(self, experiment: ExperimentDict, **kwargs) -> List[Any]:
        children = []
        for sim in experiment['simulations']:
            children.append(self.platform.get_item(sim, ItemType.SIMULATION,
                                                   experiment_id=experiment['_uid'],
                                                   raw=True,
                                                   **kwargs
                                                   )
                            )
        return children

    def get_parent(self, experiment: Any, **kwargs) -> Experiment:
        pass

    def platform_run_item(self, experiment: Experiment, **kwargs):
        exp_path = self.get_experiment_path(experiment.uid)
        path = os.path.join(exp_path, "experiment.json")
        os.makedirs(exp_path, exist_ok=True)
        if not os.path.exists(path):
            with open(path, 'w') as out:
                out.write(json.dumps(experiment.to_dict(), cls=IDMJSONEncoder))
        for sim in experiment.simulations:
            if sim.status in [None, EntityStatus.CREATED]:
                self.platform._simulations.run_item(sim)

    def get_experiment_path(self, experiment_id: Union[str]) -> str:
        """
        Get path to experiment directory

        Args:
            experiment_id:

        Returns:

        """
        return os.path.join(self.platform.execute_directory, str(experiment_id))

    @staticmethod
    def download_asset(path):
        logger.info(f"Downloading asst from {path}")
        if not os.path.exists(path):
            logger.error(f"Cannot the asset {path}")
            raise FileNotFoundError(f"Cannot the asset {path}")
        with open(path, 'rb') as i:
            while True:
                res = i.read(128)
                if res:
                    yield res
                else:
                    break

    def send_assets(self, experiment: Experiment, **kwargs):
        # calculate total md5 of all files
        md5 = hashlib.md5()
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
                with open(asset.absolute_path) as ifi:
                    self.__calculate_partial_md5(ifi, md5)
                shutil.copy(asset.absolute_path, remote_path)
            else:
                ifi = io.BytesIO(asset.content.encode('utf-8') if isinstance(asset.content, str) else asset.content)
                self.__calculate_partial_md5(ifi, md5)
                if logger.isEnabledFor(DEBUG):
                    logger.debug(f"Writing {asset.absolute_path} to {remote_path}")
                with open(remote_path, 'wb') as out:
                    if isinstance(asset.content, str):
                        out.write(asset.content.encode('utf-8'))
                    else:
                        out.write(asset.content)

        experiment.assets.platform_id = md5.hexdigest()

    def __calculate_partial_md5(self, ifi, md5):
        while True:
            chunk = ifi.read(8196)
            if not chunk:
                break
            else:
                if isinstance(chunk, bytes):
                    md5.update(chunk)
                else:
                    md5.update(chunk.encode('utf-8'))

    def refresh_status(self, experiment: Experiment, **kwargs):
        if logger.isEnabledFor(DEBUG):
            logger.debug(f'Refreshing status for Experiment: {experiment.uid}')
        for simulation in self.platform._simulations.simulations.get(experiment.uid):
            for esim in experiment.simulations:
                if esim == simulation:
                    logger.debug(f'Setting {simulation.uid} Status to {simulation.status}')
                    esim.status = simulation.status
                    break

    def list_assets(self, experiment: Experiment, children: bool = False,
                    **kwargs) -> List[Asset]:
        """
        List assets for the experiment

        Args:
            experiment:
            children:
            **kwargs:

        Returns:

        """
        logger.info("Listing assets for experiment")
        assets = []
        asset_path = os.path.join(self.get_experiment_path(experiment.uid), "Assets")
        for root, files, dirs in os.walk(asset_path):
            for file in files:
                fp = os.path.join(asset_path, file)
                asset = Asset(absolute_path=fp, filename=file)
                assets.append(asset)

        if children:
            for sim in experiment.simulations:
                assets.extend(self.platform._simulations.list_assets(sim))
        return assets

    def to_entity(self, data: Dict[Any, Any], parent: Optional[Any] = None, children: bool = True, **kwargs) -> \
            Experiment:
        excluded = ['platform_id', 'item_type', 'frozen', 'simulations']
        experiment = Experiment(**{k: v for k, v in data.items() if k not in excluded})
        experiment.platform_metadata = data
        if data['assets']:
            assets = AssetCollection()
            exp_path = os.path.join(self.get_experiment_path(experiment.uid), "Assets")
            for root, dirs, files in os.walk(exp_path):
                for file in files:
                    fp = os.path.abspath(os.path.join(root, file))
                    asset = Asset(absolute_path=fp, filename=file)
                    asset.download_generator_hook = partial(file_contents_to_generator, fp)
                    assets.add_asset(asset)
            experiment.assets = assets
        if children:
            experiment.simulations = self.platform.get_children(
                experiment.uid,
                ItemType.EXPERIMENT,
                item=experiment,
                **kwargs
            )

        return experiment

    def platform_modify_experiment(self, experiment: Experiment, regather_common_assets: bool = False, **kwargs) -> Experiment:
        experiment.pre_creation(self.platform, gather_assets=regather_common_assets)
        EXPERIMENTS_LOCK.acquire()
        self.experiments[experiment.uid] = experiment
        EXPERIMENTS_LOCK.release()
        self.send_assets(experiment)
        return experiment
