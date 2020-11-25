import json
import os
import shutil
import sys
from concurrent.futures._base import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import field, dataclass
from logging import getLogger, DEBUG
from pathlib import PurePath
from typing import List, Dict, Any, Type
from uuid import UUID, uuid4

from jinja2 import Environment
from tqdm import tqdm
from idmtools.assets import Asset
from idmtools.core import EntityStatus
from idmtools.entities.iplatform_ops.iplatform_simulation_operations import IPlatformSimulationOperations
from idmtools.entities.simulation import Simulation
from idmtools.utils.json import IDMJSONEncoder

logger = getLogger(__name__)


# Class to distinguish between regular AC and our platform and for type mapping on the platform
class FilePlatformSimulation(Simulation):
    pass


@dataclass
class FilePlatformSimulationOperations(IPlatformSimulationOperations):
    platform: 'FilePlatform'  # noqa F821
    platform_type: Type = field(default=FilePlatformSimulation)

    def get(self, simulation_id: UUID, **kwargs) -> Any:
        pass

    def platform_create(self, simulation: Simulation, index: int = None, simulation_prefix_str: str = None, add_metadata: bool = None, **kwargs) -> Any:
        parent_directory = PurePath(simulation.parent._metadata['output_directory'])
        simulation.uid = uuid4()
        if simulation_prefix_str or self.platform.simulation_prefix_str:
            sf = simulation_prefix_str if simulation_prefix_str else self.platform.simulation_prefix_str
            print(sf)
            print(simulation.tags)
            sn = sf.format(item=simulation, i=index)
            output_directory = parent_directory.joinpath(sn)
        else:
            sn = str(index)
            output_directory = parent_directory.joinpath(sn)

        # set on object so children can see it later
        simulation._metadata = dict(output_directory=output_directory, sn=sn)

        if self.platform.write_scripts:
            env = Environment()
            script_template = env.from_string(self.platform.simulation_exec_template)
            if logger.isEnabledFor(DEBUG):
                logger.debug("Rendering template using vars {simulation}, {task}, {platform}".format(simulation=str(simulation), platform=str(self.platform), task=str(simulation.task)))
            result = script_template.render(simulation=simulation, platform=self.platform, task=simulation.task, env=os.environ)
            simulation.add_asset(Asset(filename="run.sh", content=result))

        if add_metadata or self.platform.add_metadata:
            metadata = json.dumps(simulation.to_dict(), cls=IDMJSONEncoder)
            simulation.add_asset(Asset(filename="simulation_metadata.json", content=metadata))

        if simulation.parent._metadata.get('archive', None) is None:
            parent_assets = parent_directory.joinpath("Assets")
            td = output_directory.joinpath("Assets")
            if self.platform.use_links:
                os.makedirs(output_directory, exist_ok=True)
                if logger.isEnabledFor(DEBUG):
                    logger.debug(f"Linking Experiment assets from {parent_assets} -> {td}")
                os.symlink(parent_assets, td)
            elif self.platform.copy_experiment_assets:
                if logger.isEnabledFor(DEBUG):
                    logger.debug(f"Copying experiment assets {parent_assets} -> {td}")
                os.makedirs(output_directory, exist_ok=True)
                shutil.copytree(parent_assets, td)
        self.send_assets(simulation)
        return simulation

    def batch_create(self, sims: List[Simulation], display_progress: bool = True, **kwargs) -> List[Simulation]:
        pool = ThreadPoolExecutor()
        futures = []
        for index, simulation in tqdm(enumerate(sims)):
            futures.append(pool.submit(self.create, simulation, index=index, **kwargs))
        return [f.result() for f in tqdm(as_completed(futures), total=len(futures))]

    def get_parent(self, simulation: Any, **kwargs) -> Any:
        pass

    def platform_run_item(self, simulation: Simulation, **kwargs):
        simulation.status = EntityStatus.SUCCEEDED

    def send_assets(self, simulation: Any, **kwargs):
        self.platform._assets.platform_create(simulation.assets, parent=simulation, **kwargs)

    def refresh_status(self, simulation: Simulation, **kwargs):
        pass

    def get_assets(self, simulation: Simulation, files: List[str], **kwargs) -> Dict[str, bytearray]:
        pass

    def list_assets(self, simulation: Simulation, **kwargs) -> List[Asset]:
        pass
