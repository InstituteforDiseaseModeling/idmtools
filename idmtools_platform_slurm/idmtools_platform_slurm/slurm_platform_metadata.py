from collections import defaultdict
from dataclasses import dataclass
from typing import NoReturn, Any, List
from uuid import UUID

from idmtools.core import ItemType
from idmtools.entities import IExperiment
from idmtools.entities.iplatform_metadata import IPlaformMetdataOperations
from idmtools_platform_slurm.slurm_operations import SlurmOperations, SLURM_STATES


@dataclass(init=False)
class SlurmPlaformMetdataOperations(IPlaformMetdataOperations):
    parent: 'SlurmPlatform'
    _op_client: SlurmOperations

    def __init__(self, parent: 'SlurmPlatform', op_client):
        self.parent = parent
        self._op_client = op_client

    def refresh_status(self, item) -> NoReturn:
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

    def get_platform_item(self, item_id: UUID, item_type: ItemType, **kwargs) -> Any:
        raise NotImplementedError("Metadata not supported currently")

    def get_children_for_platform_item(self, platform_item: Any, raw: bool, **kwargs) -> List[Any]:
        raise NotImplementedError("Metadata not supported currently")

    def get_parent_for_platform_item(self, platform_item: Any, raw: bool, **kwargs) -> Any:
        raise NotImplementedError("Metadata not supported currently")

    def restore_simulations(self, experiment: IExperiment) -> None:
        raise NotImplementedError("Metadata restoration need to be implemented")