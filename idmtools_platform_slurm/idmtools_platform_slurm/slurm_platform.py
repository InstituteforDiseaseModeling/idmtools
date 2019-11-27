import os
import typing
from typing import Optional, List, Any
from collections import defaultdict
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass, field
from logging import getLogger
from multiprocessing import cpu_count
from uuid import uuid4, UUID

from idmtools.core import ItemType
from idmtools.core.interfaces.ientity import TEntityList
from idmtools.core.interfaces.iitem import TItem, TItemList
from idmtools.entities import IPlatform
from idmtools.entities.iexperiment import TExperiment, IExperiment, IHostBinaryExperiment, IWindowsExperiment, \
    ILinuxExperiment, IDockerExperiment
from idmtools.entities.isimulation import TSimulation, ISimulation, TSimulationBatch
from idmtools_platform_slurm.slurm_operations import SlurmOperationalMode, SlurmOperations, \
    RemoteSlurmOperations, LocalSlurmOperations, SLURM_STATES

logger = getLogger(__name__)


@dataclass
class SlurmPlatform(IPlatform):

    job_directory: str = None
    mode: SlurmOperationalMode = None
    mail_type: Optional[str] = None
    mail_user: Optional[str] = None

    # options for ssh mode
    remote_host: Optional[str] = None
    remote_port: int = 22
    remote_user: Optional[str] = None
    key_file: Optional[str] = None

    _op_client: SlurmOperations = field(default=None, metadata={"pickle_ignore": True})

    def __post_init__(self):
        super().__post_init__()
        if self.job_directory is None:
            raise ValueError("Job Directory is required")

        self.mode = SlurmOperationalMode[self.mode.upper()]
        if self.mode == SlurmOperationalMode.SSH:
            if self.remote_host is None or self.remote_user is None:
                raise ValueError("remote_host, remote_user and key_file are required configuration parameters "
                                 "when the mode is SSH")
            self._op_client = RemoteSlurmOperations(self.remote_host, self.remote_user, self.key_file,
                                                    port=self.remote_port)
        else:
            self._op_client = LocalSlurmOperations()

    def __create_experiment(self, experiment: TExperiment) -> None:
        experiment.uid = str(uuid4())
        exp_dir = os.path.join(self.job_directory, experiment.uid)
        self._op_client.mk_directory(exp_dir)
        # store job info in the directory
        self._op_client.dump_metadata(experiment, os.path.join(exp_dir, 'experiment.json'))
        self.send_assets(experiment)

    def __create_simulations(self, simulations_batch: TSimulationBatch) -> List[Any]:
        ids = []

        common_asset_dir = os.path.join(self.job_directory, simulations_batch[0].experiment.uid, 'Assets')

        for simulation in simulations_batch:
            simulation.uid = str(uuid4())
            sim_dir = os.path.join(self.job_directory, simulation.experiment.uid, simulation.uid)
            self._op_client.mk_directory(sim_dir)
            # store sim info in folder
            self._op_client.dump_metadata(simulation, os.path.join(sim_dir, 'simulation.json'))
            self._op_client.link_dir(common_asset_dir, os.path.join(sim_dir, 'Assets'))
            self.send_assets(simulation)
            ids.append(simulation.uid)
            self._op_client.create_simulation_batch_file(simulation, sim_dir, mail_type=self.mail_type,
                                                         mail_user=self.mail_user)
        return ids

    def restore_simulations(self, experiment: TExperiment) -> None:
        raise NotImplementedError("Metadata restoration need to be implemented")

    def __has_singularity(self):
        """
        Do we support singularity
        Returns:

        """
        # TODO Full Implementation
        return False

    def _create_batch(self, batch: TEntityList, item_type: ItemType) -> List[UUID]:
        if item_type == ItemType.SIMULATION:
            ids = self.__create_simulations(simulations_batch=batch)
        elif item_type == ItemType.EXPERIMENT:
            ids = [self.__create_experiment(experiment=item) for item in batch]

        return ids

    def run_items(self, items: TItemList) -> typing.NoReturn:
        for item in items:
            if item.item_type == ItemType.EXPERIMENT:
                if not self.is_supported_experiment(item):
                    raise ValueError("This experiment type is not support on the LocalPlatform.")
                for simulation in item.simulations:
                    sim_dir = os.path.join(self.job_directory, simulation.experiment.uid, simulation.uid)
                    self._op_client.submit_job(os.path.join(sim_dir, 'submit-simulation.sh'), sim_dir)
            else:
                raise Exception(f'Unable to run item id: {item.uid} of type: {type(item)} ')

    def send_assets(self, item: 'TItem', **kwargs) -> 'NoReturn':
        if isinstance(item, IExperiment):
            for asset in item.assets:
                exp_asset_dir = os.path.join(self.job_directory, item.uid, 'Assets')
                self._op_client.mk_directory(exp_asset_dir)
                self._op_client.copy_asset(asset, exp_asset_dir)
        elif isinstance(item, ISimulation):
            # Go through all the assets
            for asset in item.assets:
                sim_dir = os.path.join(self.job_directory, item.experiment.uid, item.uid)
                self._op_client.copy_asset(asset, sim_dir)
        else:
            raise NotImplementedError("Only assests for Experiments and Simulations implemented")

    def refresh_status(self, item) -> 'NoReturn':
        if isinstance(item, IExperiment):
            states = defaultdict(int)
            sim_states = self._op_client.experiment_status(item)
            for s in item.simulations:
                if s.uid in sim_states:
                    s.status = SLURM_STATES[sim_states[s.uid]]
                states[s.status] += 1

            return item
        else:
            raise NotImplementedError("Need to implement loading slurm states of sim directly")

    def get_platform_item(self, item_id: 'UUID', item_type: 'ItemType', **kwargs) -> 'Any':
        pass

    def get_children_for_platform_item(self, platform_item: 'Any', raw: 'bool', **kwargs) -> List[Any]:
        raise NotImplementedError("Metadata not supported currently")

    def get_parent_for_platform_item(self, platform_item: 'Any', raw: 'bool', **kwargs) -> Any:
        raise NotImplementedError("Metadata not supported currently")

    def get_files(self, item: TItem, files: List[str]) -> typing.Dict[str, bytearray]:
        ret = dict()
        futures = {}
        with ThreadPoolExecutor(max_workers=cpu_count()) as pool:
            if isinstance(item, IExperiment):
                base_path = os.path.join(self.job_directory, item.uid)
                for file in files:
                    futures[pool.submit(self._op_client.download_asset, os.path.join(file, base_path))] = file
            elif isinstance(item, ISimulation):
                base_path = os.path.join(self.job_directory, item.parent_id, item.uid)
                for file in files:
                    futures[pool.submit(self._op_client.download_asset, os.path.join(file, base_path))] = file
            for future in as_completed(futures):
                ret[futures[future]] = future.result()
        return ret

    def supported_experiment_types(self) -> List[typing.Type]:
        supported = [IExperiment, IHostBinaryExperiment, ILinuxExperiment]
        if self.__has_singularity():
            supported.append(IDockerExperiment)
        return supported

    def unsupported_experiment_types(self) -> List[typing.Type]:
        supported = [IWindowsExperiment]
        if not self.__has_singularity():
            supported.append(IDockerExperiment)
        return supported

