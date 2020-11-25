import json
from logging import getLogger
import os
from dataclasses import field, dataclass
from threading import Lock
from pathlib import PurePath
from typing import Any, List, Type, Optional
from uuid import UUID, uuid4
from zipfile import ZipFile, ZIP_LZMA

from tqdm import tqdm
from idmtools.assets import Asset
from idmtools.core import EntityStatus
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform_ops.iplatform_experiment_operations import IPlatformExperimentOperations
from idmtools.utils.json import IDMJSONEncoder
from idmtools_platform_file._api.utils import create_next_dir

logger = getLogger(__name__)


# Class to distinguish between regular AC and our platform and for type mapping on the platform
class FilePlatformExperiment(Experiment):
    pass


EXPERIMENT_LOCKS = dict()


@dataclass
class FilePlatformExperimentOperations(IPlatformExperimentOperations):
    platform: 'FilePlatform'  # noqa F821
    platform_type: Type = field(default=FilePlatformExperiment)

    def get(self, experiment_id: UUID, **kwargs) -> Any:
        pass

    def platform_create(self, experiment: Experiment, experiment_prefix_str: Optional[str] = None, output_directory: str = None, is_archive: bool = True, use_links: bool = None, add_metadata: bool = None, **kwargs) -> Any:
        output_directory = PurePath(output_directory if output_directory else self.platform.output_directory)
        experiment.uid = uuid4()
        if experiment_prefix_str or self.platform.experiment_prefix_str:
            output_directory = create_next_dir(output_directory, item=experiment, format_name_str=experiment_prefix_str if experiment_prefix_str else self.platform.experiment_prefix_str)
        else:
            output_directory = output_directory.joinpath(experiment.id)
        # set on object so children can see it later
        experiment._metadata = dict(output_directory=output_directory)

        if use_links or self.platform.use_links:
            experiment._metadata['use_links'] = True

        if add_metadata or self.platform.add_metadata:
            metadata = json.dumps(experiment.to_dict(exclude=['parent', 'simulations']), cls=IDMJSONEncoder)
            experiment.add_asset(Asset(filename="experiment_metadata.json", content=metadata))

        if is_archive:
            EXPERIMENT_LOCKS[experiment.uid] = Lock()
            archive_file = ZipFile(PurePath(output_directory).joinpath("simulations.zip"), mode="w", compression=ZIP_LZMA)
            experiment._metadata['archive'] = archive_file

        self.send_assets(experiment)
        return experiment

    def get_children(self, experiment: Any, **kwargs) -> List[Any]:
        pass

    def get_parent(self, experiment: Any, **kwargs) -> Any:
        pass

    def platform_run_item(self, experiment: Experiment, **kwargs):
        if experiment._metadata.get('archive', None):
            experiment._metadata.get('archive').close()
        for simulation in tqdm(experiment.simulations.items):
            simulation.status = EntityStatus.SUCCEEDED

    def send_assets(self, experiment: Any, **kwargs):
        os.makedirs(experiment._metadata['output_directory'], exist_ok=True)
        self.platform._assets.platform_create(experiment.assets, parent=experiment)

    def refresh_status(self, experiment: Experiment, **kwargs):
        pass
