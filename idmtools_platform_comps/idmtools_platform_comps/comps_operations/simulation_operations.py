from dataclasses import dataclass, field
from functools import partial
from logging import getLogger, DEBUG
from typing import Any, List, Dict, Type
from uuid import UUID
from COMPS.Data import Simulation as COMPSSimulation, QueryCriteria, Experiment as COMPSExperiment, SimulationFile, \
    Configuration
from idmtools.core import ItemType
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform_ops.iplatform_simulation_operations import IPlatformSimulationOperations
from idmtools.entities.iplatform_ops.utils import batch_create_items
from idmtools.entities.simulation import Simulation
from idmtools_platform_comps.utils.general import convert_comps_status, get_asset_for_comps_item

logger = getLogger(__name__)


def comps_batch_worker(sims: List[Simulation], interface: 'CompsPlatformSimulationOperations', num_cores,
                       priority) -> List[COMPSSimulation]:
    if logger.isEnabledFor(DEBUG):
        logger.debug(f'Create {len(sims)}')

    created_simulations = []

    for simulation in sims:
        if simulation.status is None:
            interface.pre_create(simulation)
            simulation.platform = interface.platform
            simulation._platform_object = interface.to_comps_sim(num_cores, priority, simulation)
            created_simulations.append(simulation._platform_object)
    COMPSSimulation.save_all(None, save_semaphore=COMPSSimulation.get_save_semaphore())
    for simulation in sims:
        simulation.uid = simulation.get_platform_object().id
        simulation.status = convert_comps_status(simulation.get_platform_object().state)
        interface.post_create(simulation)
    return sims


@dataclass
class CompsPlatformSimulationOperations(IPlatformSimulationOperations):
    platform: 'COMPSPlaform'  # noqa F821
    platform_type: Type = field(default=COMPSSimulation)

    def get(self, simulation_id: UUID, **kwargs) -> COMPSSimulation:
        cols = kwargs.get('columns')
        children = kwargs.get('children')
        cols = cols or ["id", "name", "experiment_id", "state"]
        children = children if children is not None else ["tags", "configuration"]
        return COMPSSimulation.get(id=simulation_id,
                                   query_criteria=QueryCriteria().select(cols).select_children(children))

    def platform_create(self, simulation: Simulation, num_cores: int = None, priority: str = None,
                        check_command: bool = True) -> COMPSSimulation:
        from idmtools_platform_comps.utils.python_version import platform_task_hooks
        if check_command:
            simulation.task = platform_task_hooks(simulation.task, self.platform)
        s = self.to_comps_sim(num_cores, priority, simulation)
        COMPSSimulation.save(s, save_semaphore=COMPSSimulation.get_save_semaphore())
        return s

    def to_comps_sim(self, num_cores, priority, simulation, config: Configuration = None):
        if config is None:
            config = self.get_simulation_config_from_simulation(num_cores, priority, simulation)
        s = COMPSSimulation(name=simulation.experiment.name, experiment_id=simulation.parent_id,
                            configuration=config)

        self.send_assets(simulation, s)
        s.set_tags(simulation.tags)
        simulation._platform_object = self.platform
        return s

    def get_simulation_config_from_simulation(self, num_cores, priority, simulation):
        comps_configuration = dict()
        if simulation.experiment.assets.count != 0:
            comps_configuration['asset_collection_id'] = simulation.experiment.assets.uid
        comps_exp: COMPSExperiment = simulation.parent.get_platform_object()
        comps_exp_config: Configuration = comps_exp.configuration
        if num_cores is not None and num_cores != comps_exp_config.max_cores:
            logger.info(f'Overriding cores for sim to {num_cores}')
            comps_configuration['max_cores'] = num_cores
            comps_configuration['min_cores'] = num_cores
        if priority is not None and priority != comps_exp_config.priority:
            logger.info(f'Overriding priority for sim to {priority}')
            comps_configuration['priority'] = priority
        if comps_exp_config.executable_path != simulation.task.command.executable:
            logger.info(f'Overriding executable_path for sim to {simulation.task.command.executable}')
            comps_configuration['executable_path'] = simulation.task.command.executable
        sim_task = simulation.task.command.arguments + " " + simulation.task.command.options
        if comps_exp_config.simulation_input_args != sim_task:
            logger.info(f'Overriding simulation_input_args for sim to {sim_task}')
            comps_configuration['simulation_input_args'] = sim_task
        if logger.isEnabledFor(DEBUG):
            logger.debug(f'Simulation config: {str(comps_configuration)}')
        return Configuration(**comps_configuration)

    def batch_create(self, sims: List[Simulation], num_cores: int = None, priority: str = None) -> \
            List[COMPSSimulation]:
        thread_func = partial(comps_batch_worker, interface=self, num_cores=num_cores, priority=priority)
        return batch_create_items(sims,
                                  batch_worker_thread_func=thread_func,
                                  progress_description="Creating Simulations on Comps")

    def get_parent(self, simulation: Any, **kwargs) -> COMPSExperiment:
        return self.platform._experiments.get(simulation.experiment_id, **kwargs) if simulation.experiment_id else None

    def platform_run_item(self, simulation: Simulation, **kwargs):
        pass

    def send_assets(self, simulation: Simulation, comps_sim: COMPSSimulation = None, **kwargs):
        if comps_sim is None:
            comps_sim = simulation.get_platform_object()
        for asset in simulation.assets:
            comps_sim.add_file(simulationfile=SimulationFile(asset.filename, 'input'), data=asset.bytes)

    def refresh_status(self, simulation: Simulation, **kwargs):
        s = COMPSSimulation.get(id=simulation.uid, query_criteria=QueryCriteria().select(['state']))
        simulation.status = convert_comps_status(s.state)

    def to_entity(self, simulation: Any, parent: Experiment = None, **kwargs) -> Simulation:
        # Recreate the experiment if needed
        if parent is None:
            parent = self.platform.get_item(simulation.experiment_id, item_type=ItemType.EXPERIMENT)
        # Get a simulation
        obj = Simulation()
        obj.platform = self.platform
        obj.parent = parent
        obj.experiment = parent
        # Set its correct attributes
        obj.uid = simulation.id
        obj.tags = simulation.tags
        obj.status = convert_comps_status(simulation.state)
        return obj

    def get_assets(self, simulation: Simulation, files: List[str], **kwargs) -> Dict[str, bytearray]:
        return get_asset_for_comps_item(self.platform, simulation, files, self.cache)

    def list_assets(self, simulation: Simulation, **kwargs) -> List[str]:
        comps_sim: COMPSSimulation = simulation.get_platform_object(True, children=["files", "configuration"])
        return comps_sim.files
