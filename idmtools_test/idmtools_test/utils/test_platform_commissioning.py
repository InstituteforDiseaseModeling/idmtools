from logging import getLogger
from typing import NoReturn, List
from uuid import UUID, uuid4
import diskcache
from idmtools.core import ItemType, EntityStatus
from idmtools.core.interfaces.ientity import IEntityList
from idmtools.core.interfaces.iitem import IItemList
from idmtools.entities import IExperiment
from idmtools.entities.iplatform import IPlatformCommissioningOperations

logger = getLogger(__name__)


class TestPlatformCommissioningOperations(IPlatformCommissioningOperations):
    parent: 'TestPlatform'

    def run_items(self, items: IItemList) -> NoReturn:
        for item in items:
            if item.item_type == ItemType.EXPERIMENT:
                self.parent.metadata.set_simulation_status(item.uid, EntityStatus.RUNNING)

    def _create_batch(self, batch: IEntityList, item_type: ItemType) -> List[UUID]:
        if item_type == ItemType.SIMULATION:
            return self._create_simulations(simulation_batch=batch)

        if item_type == ItemType.EXPERIMENT:
            return [self._create_experiment(experiment=item) for item in batch]

    def _create_experiment(self, experiment: IExperiment) -> UUID:
        if not self.parent.is_supported_experiment(experiment):
            raise ValueError("The specified experiment is not supported on this platform")
        uid = uuid4()
        experiment.uid = uid
        self.parent.metadata.experiments.set(uid, experiment)
        lock = diskcache.Lock(self.parent.metadata.simulations, 'simulations-lock')
        with lock:
            self.parent.metadata.simulations.set(uid, list())
        logger.debug(f"Created Experiment {experiment.uid}")
        return experiment.uid

    def _create_simulations(self, simulation_batch: IEntityList):

        simulations = []
        for simulation in simulation_batch:
            experiment_id = simulation.parent_id
            simulation.uid = uuid4()
            simulations.append(simulation)

        lock = diskcache.Lock(self.parent.metadata.simulations, 'simulations-lock')
        with lock:
            existing_simulations = self.parent.metadata.simulations.pop(experiment_id)
            self.parent.metadata.simulations[experiment_id] = existing_simulations + simulations
        return [s.uid for s in simulations]
