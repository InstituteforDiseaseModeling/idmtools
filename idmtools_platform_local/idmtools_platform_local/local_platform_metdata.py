import logging
from dataclasses import dataclass
from typing import NoReturn, Any, List
from uuid import UUID
from idmtools.core import ItemType
from idmtools.core.experiment_factory import experiment_factory
from idmtools.entities import ISimulation, IExperiment
from idmtools.entities.iplatform import IPlaformMetdataOperations
from idmtools_platform_local.client.experiments_client import ExperimentsClient
from idmtools_platform_local.client.simulations_client import SimulationsClient

logger = logging.getLogger(__name__)

status_translate = dict(
    created='CREATED',
    in_progress='RUNNING',
    canceled='FAILED',
    failed='FAILED',
    done='SUCCEEDED'
)


def local_status_to_common(status):
    from idmtools.core import EntityStatus
    return EntityStatus[status_translate[status]]


@dataclass
class LocalPlatformMetaDataOperations(IPlaformMetdataOperations):
    parent: 'LocalPlatform'

    def refresh_status(self, item) -> NoReturn:
        """
        Refresh the status of the specified item

        """
        if isinstance(item, ISimulation):
            raise Exception(f'Unknown how to refresh items of type {type(item)} '
                            f'for platform: {self.__class__.__name__}')
        elif isinstance(item, IExperiment):
            status = SimulationsClient.get_all(experiment_id=item.uid, per_page=9999)
            for s in item.simulations:
                sim_status = [st for st in status if st['simulation_uid'] == s.uid]

                if sim_status:
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f"Simulation {sim_status[0]['simulation_uid']}status: {sim_status[0]['status']}")
                    s.status = local_status_to_common(sim_status[0]['status'])

    def get_platform_item(self, item_id: UUID, item_type: ItemType, **kwargs) -> Any:
        if item_type == ItemType.EXPERIMENT:
            experiment_dict = ExperimentsClient.get_one(item_id)
            experiment = experiment_factory.create(experiment_dict['tags'].get("type"), tags=experiment_dict['tags'])
            experiment.uid = experiment_dict['experiment_id']
            return experiment
        elif item_type == ItemType.SIMULATION:
            simulation_dict = SimulationsClient.get_one(item_id)
            experiment = self.get_platform_item(simulation_dict["experiment_id"], ItemType.EXPERIMENT)
            simulation = experiment.simulation()
            simulation.uid = simulation_dict['simulation_uid']
            simulation.tags = simulation_dict['tags']
            simulation.status = local_status_to_common(simulation_dict['status'])
            return simulation

    def get_children_for_platform_item(self, platform_item: Any, raw: bool, **kwargs) -> List[Any]:
        if isinstance(platform_item, IExperiment):
            platform_item.simulations.clear()

            # Retrieve the simulations for the current page
            simulation_dict = SimulationsClient.get_all(experiment_id=platform_item.uid, per_page=9999)

            # Add the simulations
            for sim_info in simulation_dict:
                sim = platform_item.simulation()
                sim.uid = sim_info['simulation_uid']
                sim.tags = sim_info['tags']
                sim.status = local_status_to_common(sim_info['status'])
                platform_item.simulations.append(sim)

            return platform_item.simulations

    def get_parent_for_platform_item(self, platform_item: Any, raw: bool, **kwargs) -> Any:
        if isinstance(platform_item, ISimulation):
            return self.get_platform_item(platform_item.parent_id, ItemType.EXPERIMENT)
        return None
