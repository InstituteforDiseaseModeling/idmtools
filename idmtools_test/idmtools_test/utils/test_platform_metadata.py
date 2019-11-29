import os
from dataclasses import dataclass, field
from logging import getLogger
from typing import NoReturn, Any, List
from uuid import UUID
import diskcache
import numpy as np
from idmtools.core import ItemType
from idmtools.entities.iplatform import IPlaformMetdataOperations

logger = getLogger(__name__)
current_directory = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.abspath(os.path.join(current_directory, "..", "data"))


@dataclass
class TestPlatformMetadataOperations(IPlaformMetdataOperations):
    experiments: 'diskcache.Cache' = field(default=None, compare=False, metadata={"pickle_ignore": True})
    simulations: 'diskcache.Cache' = field(default=None, compare=False, metadata={"pickle_ignore": True})

    def __post_init__(self):
        os.makedirs(data_path, exist_ok=True)
        self.initialize_test_cache()

    def initialize_test_cache(self):
        """
        Create a cache experiments/simulations that will only exist during test
        """
        self.experiments = diskcache.Cache(os.path.join(data_path, 'experiments_test'))
        self.simulations = diskcache.Cache(os.path.join(data_path, 'simulations_test'))

    def cleanup(self):
        for cache in [self.experiments, self.simulations]:
            cache.clear()
            cache.close()

    def refresh_status(self, item) -> NoReturn:
        for simulation in self.simulations.get(item.uid):
            for esim in item.simulations():
                if esim == simulation:
                    esim.status = simulation.status
                    break

    def get_platform_item(self, item_id: UUID, item_type: ItemType, **kwargs) -> Any:
        obj = None
        if item_type == ItemType.SIMULATION:
            for eid in self.simulations:
                sims = self.simulations.get(eid)
                if sims:
                    for sim in self.simulations.get(eid):
                        if sim.uid == item_id:
                            obj = sim
                            break
                if obj:
                    break
        elif item_type == ItemType.EXPERIMENT:
            obj = self.experiments.get(item_id)

        if not obj:
            logger.warning(f"Could not find object with id: {item_id}")
            return

        obj.platform = self.parent
        return obj

    def get_children_for_platform_item(self, platform_item: Any, raw: bool, **kwargs) -> List[Any]:
        if platform_item.item_type == ItemType.EXPERIMENT:
            return self.simulations.get(platform_item.uid)

    def get_parent_for_platform_item(self, platform_item: Any, raw: bool, **kwargs) -> Any:
        if platform_item.item_type == ItemType.SIMULATION:
            return self.experiments.get(platform_item.parent_id)

    def set_simulation_status(self, experiment_uid, status):
        self.set_simulation_prob_status(experiment_uid, {status: 1})

    def set_simulation_prob_status(self, experiment_uid, status):
        simulations = self.simulations.get(experiment_uid)
        for simulation in simulations:
            new_status = np.random.choice(
                a=list(status.keys()),
                p=list(status.values())
            )
            simulation.status = new_status
        self.simulations.set(experiment_uid, simulations)

    def set_simulation_num_status(self, experiment_uid, status, number):
        simulations = self.simulations.get(experiment_uid)
        for simulation in simulations:
            simulation.status = status
            self.simulations.set(experiment_uid, simulations)
            number -= 1
            if number <= 0:
                return
