import os
from dataclasses import dataclass
from typing import NoReturn, List, Any
from uuid import UUID, uuid4

from idmtools.core import ItemType
from idmtools.core.interfaces.ientity import IEntityList
from idmtools.core.interfaces.iitem import IItemList
from idmtools.entities import IExperiment
from idmtools.entities.iplatform_commissioning import IPlatformCommissioningOperations
from idmtools.entities.isimulation import TSimulationBatch
from idmtools_platform_slurm.slurm_operations import SlurmOperations


@dataclass(init=False)
class SlurmPlatformCommissioningOperations(IPlatformCommissioningOperations):
    parent: 'SlurmPlatform'
    _op_client: SlurmOperations

    def __init__(self, parent: 'SlurmPlatform', op_client):
        self.parent = parent
        self._op_client = op_client

    def run_items(self, items: IItemList) -> NoReturn:
        for item in items:
            if item.item_type == ItemType.EXPERIMENT:
                if not self.parent.is_supported_experiment(item):
                    raise ValueError("This experiment type is not support on the LocalPlatform.")
                for simulation in item.simulations:
                    sim_dir = os.path.join(self.parent.job_directory, simulation.experiment.uid, simulation.uid)
                    self._op_client.submit_job(os.path.join(sim_dir, 'submit-simulation.sh'), sim_dir)
            else:
                raise Exception(f'Unable to run item id: {item.uid} of type: {type(item)} ')

    def _create_batch(self, batch: IEntityList, item_type: ItemType) -> List[UUID]:
        ids = []
        if item_type == ItemType.SIMULATION:
            ids = self.__create_simulations(simulations_batch=batch)
        elif item_type == ItemType.EXPERIMENT:
            ids = [self.__create_experiment(experiment=item) for item in batch]

        return ids

    def __create_experiment(self, experiment: IExperiment) -> None:
        experiment.uid = str(uuid4())
        exp_dir = os.path.join(self.parent.job_directory, experiment.uid)
        self.parent.io.make_directory(exp_dir)
        # store job info in the directory
        self.parent.io.dump_metadata(experiment, os.path.join(exp_dir, 'experiment.json'))
        self.parent.io.send_assets(experiment)

    def __create_simulations(self, simulations_batch: TSimulationBatch) -> List[Any]:
        ids = []

        common_asset_dir = os.path.join(self.parent.job_directory, simulations_batch[0].experiment.uid, 'Assets')

        for simulation in simulations_batch:
            simulation.uid = str(uuid4())
            sim_dir = os.path.join(self.parent.job_directory, simulation.experiment.uid, simulation.uid)
            self.parent.io.make_directory(sim_dir)
            # store sim info in folder
            self.parent.io.dump_metadata(simulation, os.path.join(sim_dir, 'simulation.json'))
            self.parent.io.link_dir(common_asset_dir, os.path.join(sim_dir, 'Assets'))
            self.parent.io.send_assets(simulation)
            ids.append(simulation.uid)
            self._op_client.create_simulation_batch_file(simulation, sim_dir, mail_type=self.parent.mail_type,
                                                         mail_user=self.parent.mail_user)
        return ids