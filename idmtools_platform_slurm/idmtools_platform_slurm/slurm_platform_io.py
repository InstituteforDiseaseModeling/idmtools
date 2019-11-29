import os
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from multiprocessing import cpu_count
from typing import NoReturn, List, Dict

from idmtools.core.interfaces.iitem import IItem
from idmtools.entities import IExperiment, ISimulation
from idmtools.entities.iplatform import IPlatformIOOperations
from idmtools_platform_slurm.slurm_operations import SlurmOperations


@dataclass(init=False)
class SlurmPlatformIOOperations(IPlatformIOOperations):
    parent: 'SlurmPlatform'
    _op_client: SlurmOperations

    def __init__(self, parent: 'SlurmPlatform', op_client):
        self.parent = parent
        self._op_client = op_client

    def send_assets(self, item: IItem, **kwargs) -> NoReturn:
        if isinstance(item, IExperiment):
            for asset in item.assets:
                exp_asset_dir = os.path.join(self.parent.job_directory, item.uid, 'Assets')
                self._op_client.mk_directory(exp_asset_dir)
                self._op_client.copy_asset(asset, exp_asset_dir)
        elif isinstance(item, ISimulation):
            # Go through all the assets
            for asset in item.assets:
                sim_dir = os.path.join(self.parent.job_directory, item.experiment.uid, item.uid)
                self._op_client.copy_asset(asset, sim_dir)
        else:
            raise NotImplementedError("Only assests for Experiments and Simulations implemented")

    def get_files(self, item: IItem, files: List[str]) -> Dict[str, bytearray]:
        ret = dict()
        futures = {}
        with ThreadPoolExecutor(max_workers=cpu_count()) as pool:
            if isinstance(item, IExperiment):
                base_path = os.path.join(self.parent.job_directory, item.uid)
                for file in files:
                    futures[pool.submit(self._op_client.download_asset, os.path.join(file, base_path))] = file
            elif isinstance(item, ISimulation):
                base_path = os.path.join(self.parent.job_directory, item.parent_id, item.uid)
                for file in files:
                    futures[pool.submit(self._op_client.download_asset, os.path.join(file, base_path))] = file
            for future in as_completed(futures):
                ret[futures[future]] = future.result()
        return ret

    def make_directory(self, path) -> bool:
        return self._op_client.mk_directory(path)

    def dump_metadata(self, item: IItem, path: str):
        self._op_client.dump_metadata(item, path)

    def link_dir(self, src: str, dest: str):
        self._op_client.link_dir(src, dest)