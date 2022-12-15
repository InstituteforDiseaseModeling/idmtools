"""idmtools comps simulation operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import suppress
from threading import Lock
import time
import json
import uuid
from dataclasses import dataclass, field
from COMPS.Data.Simulation import SimulationState
from functools import partial
from logging import getLogger, DEBUG
from typing import Any, List, Dict, Type, Optional, TYPE_CHECKING
from uuid import UUID
from COMPS.Data import Simulation as COMPSSimulation, QueryCriteria, Experiment as COMPSExperiment, SimulationFile, \
    Configuration
from idmtools.assets import AssetCollection, Asset
from idmtools.core import ItemType, EntityStatus
from idmtools.core.task_factory import TaskFactory
from idmtools.entities import CommandLine
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform_ops.iplatform_simulation_operations import IPlatformSimulationOperations
from idmtools.entities.iplatform_ops.utils import batch_create_items
from idmtools.entities.simulation import Simulation
from idmtools.utils.json import IDMJSONEncoder
from idmtools_platform_comps.utils.general import convert_comps_status, get_asset_for_comps_item, clean_experiment_name
from idmtools_platform_comps.utils.scheduling import scheduled

if TYPE_CHECKING:  # pragma: no cover
    from idmtools_platform_comps.comps_platform import COMPSPlatform

logger = getLogger(__name__)
user_logger = getLogger('user')

# Track commissioning in batches
COMPS_EXPERIMENT_BATCH_COMMISSION_LOCK = Lock()
COMPS_EXPERIMENT_BATCH_COMMISSION_TIMESTAMP = 0


def comps_batch_worker(simulations: List[Simulation], interface: 'CompsPlatformSimulationOperations', executor,
                       num_cores: Optional[int] = None, priority: Optional[str] = None, asset_collection_id: str = None,
                       min_time_between_commissions: int = 10, **kwargs) -> List[COMPSSimulation]:
    """
    Run batch worker.

    Args:
        simulations: Batch of simulation to process
        interface: SimulationOperation Interface
        executor: Thread/process executor
        num_cores: Optional Number of core to allocate for MPI
        priority: Optional Priority to set to
        asset_collection_id: Override asset collection id
        min_time_between_commissions: Minimum amount of time(in seconds) between calls to commission on an experiment
        extra info for

    Returns:
        List of Comps Simulations
    """
    global COMPS_EXPERIMENT_BATCH_COMMISSION_LOCK, COMPS_EXPERIMENT_BATCH_COMMISSION_TIMESTAMP
    if logger.isEnabledFor(DEBUG):
        logger.debug(f'Converting {len(simulations)} to COMPS')
    created_simulations = []

    new_sims = 0
    for simulation in simulations:
        if simulation.status is None:
            interface.pre_create(simulation)
            new_sims += 1
            simulation.platform = interface.platform
            simulation._platform_object = interface.to_comps_sim(simulation, num_cores=num_cores, priority=priority,
                                                                 asset_collection_id=asset_collection_id, **kwargs)
            created_simulations.append(simulation)
    if logger.isEnabledFor(DEBUG):
        logger.debug(f'Finished converting to COMPS. Starting saving of {len(simulations)}')
    COMPSSimulation.save_all(None, save_semaphore=COMPSSimulation.get_save_semaphore())
    if logger.isEnabledFor(DEBUG):
        logger.debug(f'Finished saving of {len(simulations)}. Starting post_create')
    for simulation in simulations:
        simulation.uid = simulation.get_platform_object().id
        simulation.status = convert_comps_status(simulation.get_platform_object().state)
        interface.post_create(simulation)
    if logger.isEnabledFor(DEBUG):
        logger.debug(f'Finished post-create of {len(simulations)}')

    current_time = time.time()
    # check current commission queue and last commission call
    if new_sims > 0 and current_time - COMPS_EXPERIMENT_BATCH_COMMISSION_TIMESTAMP > min_time_between_commissions:
        # be aggressive in waiting on lock. Worse case, another thread triggers this near same time
        locked = COMPS_EXPERIMENT_BATCH_COMMISSION_LOCK.acquire(timeout=0.015)
        if locked:
            # do commission asynchronously. If it fine if we happen to miss a commission
            def do_commission():
                with suppress(RuntimeError):
                    simulations[0].experiment.get_platform_object().commission()

            executor.submit(do_commission)
            COMPS_EXPERIMENT_BATCH_COMMISSION_TIMESTAMP = current_time
            COMPS_EXPERIMENT_BATCH_COMMISSION_LOCK.release()
            for simulation in simulations:
                simulation.status = EntityStatus.RUNNING

    return simulations


@dataclass
class CompsPlatformSimulationOperations(IPlatformSimulationOperations):
    """Provides simuilation operations to COMPSPlatform."""
    platform: 'COMPSPlatform'  # noqa F821
    platform_type: Type = field(default=COMPSSimulation)

    def get(self, simulation_id: UUID, columns: Optional[List[str]] = None, load_children: Optional[List[str]] = None,
            query_criteria: Optional[QueryCriteria] = None, **kwargs) -> COMPSSimulation:
        """
        Get Simulation from Comps.

        Args:
            simulation_id: ID
            columns: Optional list of columns to load. Defaults to "id", "name", "experiment_id", "state"
            load_children: Optional children to load. Defaults to "tags", "configuration"
            query_criteria: Optional query_criteria object to use your own custom criteria object
            **kwargs:

        Returns:
            COMPSSimulation
        """
        columns = columns or ["id", "name", "experiment_id", "state"]
        children = load_children if load_children is not None else ["tags", "configuration", "files"]
        query_criteria = query_criteria or QueryCriteria().select(columns).select_children(children)
        return COMPSSimulation.get(
            id=simulation_id,
            query_criteria=query_criteria
        )

    def platform_create(self, simulation: Simulation, num_cores: int = None, priority: str = None,
                        enable_platform_task_hooks: bool = True, asset_collection_id: str = None, **kwargs) -> COMPSSimulation:
        """
        Create Simulation on COMPS.

        Args:
            simulation: Simulation to create
            num_cores: Optional number of MPI Cores to allocate
            priority: Priority to load
            enable_platform_task_hooks: Should platform task hoooks be ran
            asset_collection_id: Override for asset collection id on sim
            **kwargs: Expansion fields

        Returns:
            COMPS Simulation
        """
        from idmtools_platform_comps.utils.python_version import platform_task_hooks
        if enable_platform_task_hooks:
            simulation.task = platform_task_hooks(simulation.task, self.platform)
        s = self.to_comps_sim(simulation, num_cores=num_cores, priority=priority,
                              asset_collection_id=asset_collection_id, **kwargs)
        COMPSSimulation.save(s, save_semaphore=COMPSSimulation.get_save_semaphore())
        return s

    def to_comps_sim(self, simulation: Simulation, num_cores: int = None, priority: str = None,
                     config: Configuration = None, asset_collection_id: str = None, **kwargs):
        """
        Covert IDMTools object to COMPS Object.

        Args:
            simulation: Simulation object to convert
            num_cores: Optional Num of MPI Cores to allocate
            priority: Optional Priority
            config: Optional Configuration object
            asset_collection_id:
            **kwargs additional option for comps

        Returns:
            COMPS Simulation
        """
        if config is None:
            if asset_collection_id and isinstance(asset_collection_id, str):
                asset_collection_id = uuid.UUID(asset_collection_id)
            kwargs['num_cores'] = num_cores
            kwargs['priority'] = priority
            kwargs['asset_collection_id'] = asset_collection_id
            kwargs.update(simulation._platform_kwargs)
            config = self.get_simulation_config_from_simulation(simulation, **kwargs)

        if simulation.name:
            simulation.name = clean_experiment_name(simulation.name)
        s = COMPSSimulation(
            name=clean_experiment_name(simulation.experiment.name if not simulation.name else simulation.name),
            experiment_id=simulation.parent_id,
            configuration=config
        )

        self.send_assets(simulation, s, **kwargs)
        s.set_tags(simulation.tags)
        simulation._platform_object = s
        return s

    def get_simulation_config_from_simulation(self, simulation: Simulation, num_cores: int = None, priority: str = None,
                                              asset_collection_id: str = None, **kwargs) -> \
            Configuration:
        """
        Get the comps configuration for a Simulation Object.

        Args:
            simulation: Simulation
            num_cores: Optional Num of core for MPI
            priority: Optional Priority
            asset_collection_id: Override simulation asset_collection_id
            **kwargs additional option for comps

        Returns:
            Configuration
        """
        global_scheduling = kwargs.get("scheduling", False)
        sim_scheduling = getattr(simulation, 'scheduling', False)
        scheduling = global_scheduling and sim_scheduling

        comps_configuration = dict()
        if global_scheduling:
            config = getattr(self.platform, 'comps_config', {})
            comps_exp_config = Configuration(**config)
        else:
            comps_exp: COMPSExperiment = simulation.parent.get_platform_object()
            comps_exp_config: Configuration = comps_exp.configuration

        if asset_collection_id:
            comps_configuration['asset_collection_id'] = asset_collection_id
        if num_cores is not None and num_cores != comps_exp_config.max_cores:
            logger.info(f'Overriding cores for sim to {num_cores}')
            comps_configuration['max_cores'] = num_cores
            comps_configuration['min_cores'] = num_cores
        if priority is not None and priority != comps_exp_config.priority:
            logger.info(f'Overriding priority for sim to {priority}')
            comps_configuration['priority'] = priority
        if comps_exp_config.executable_path != simulation.task.command.executable:
            logger.info(f'Overriding executable_path for sim to {simulation.task.command.executable}')
            from idmtools_platform_comps.utils.python_version import platform_task_hooks
            platform_task_hooks(simulation.task, self.platform)
            comps_configuration['executable_path'] = simulation.task.command.executable
        sim_task = simulation.task.command.arguments + " " + simulation.task.command.options
        sim_task = sim_task.strip()
        if comps_exp_config.simulation_input_args != sim_task:
            logger.info(f'Overriding simulation_input_args for sim to {sim_task}')
            comps_configuration['simulation_input_args'] = sim_task
        if logger.isEnabledFor(DEBUG):
            logger.debug(f'Simulation config: {str(comps_configuration)}')
        if scheduling:
            comps_configuration.update(executable_path=None, node_group_name=None, min_cores=None, max_cores=None,
                                       exclusive=None, simulation_input_args=None)

        return Configuration(**comps_configuration)

    def batch_create(self, simulations: List[Simulation], num_cores: int = None, priority: str = None, 
                     asset_collection_id: str = None, **kwargs) -> List[COMPSSimulation]:
        """
        Perform batch creation of Simulations.

        Args:
            simulations: Simulation to create
            num_cores: Optional MPI Cores to allocate per simulation
            priority: Optional Priority
            asset_collection_id: Asset collection id for sim(overide experiment)
            **kwargs: Future expansion

        Returns:
            List of COMPSSimulations that were created
        """
        global COMPS_EXPERIMENT_BATCH_COMMISSION_TIMESTAMP
        executor = ThreadPoolExecutor()
        thread_func = partial(comps_batch_worker, interface=self, num_cores=num_cores, priority=priority,
                              asset_collection_id=asset_collection_id,
                              min_time_between_commissions=self.platform.min_time_between_commissions,
                              executor=executor, **kwargs)
        results = batch_create_items(
            simulations,
            batch_worker_thread_func=thread_func,
            progress_description="Creating Simulations on Comps",
            unit="simulation"
        )
        # Always commission again
        try:
            results[0].parent.get_platform_object().commission()
        except RuntimeError as ex:  # occasionally we hit this because double commissioning. Its ok to ignore though because that means we have already commissioned this experiment
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"COMMISSION Response: {ex.args}")
        COMPS_EXPERIMENT_BATCH_COMMISSION_TIMESTAMP = 0
        # set commission here in comps objects to prevent commission in Experiment when batching
        for sim in results:
            sim.status = EntityStatus.RUNNING
            sim.get_platform_object()._state = SimulationState.CommissionRequested
        return results

    def get_parent(self, simulation: Any, **kwargs) -> COMPSExperiment:
        """
        Get the parent of the simulation.

        Args:
            simulation: Simulation to load parent for
            **kwargs:

        Returns:
            COMPSExperiment
        """
        return self.platform._experiments.get(simulation.experiment_id, **kwargs) if simulation.experiment_id else None

    def platform_run_item(self, simulation: Simulation, **kwargs):
        """For simulations, there is no running for COMPS."""
        pass

    def send_assets(self, simulation: Simulation, comps_sim: Optional[COMPSSimulation] = None,
                    add_metadata: bool = False, **kwargs):
        """
        Send assets to Simulation.

        Args:
            simulation: Simulation to send asset for
            comps_sim: Optional COMPSSimulation object to prevent reloading it
            add_metadata: Add idmtools metadata object
            **kwargs:

        Returns:
            None
        """
        scheduling = kwargs.get("scheduling", False) and scheduled(simulation)

        if comps_sim is None:
            comps_sim = simulation.get_platform_object()
        for asset in simulation.assets:
            if asset.filename.lower() == 'workorder.json' and scheduling:
                comps_sim.add_file(simulationfile=SimulationFile(asset.filename, 'WorkOrder'), data=asset.bytes)
            else:
                comps_sim.add_file(simulationfile=SimulationFile(asset.filename, 'input'), data=asset.bytes)

        # add metadata
        if add_metadata:
            if logger.isEnabledFor(DEBUG):
                logger.debug("Creating idmtools metadata for simulation and task on COMPS")
            # later we should add some filtering for passwords and such here in case anything weird happens
            metadata = json.dumps(simulation.task.to_dict(), cls=IDMJSONEncoder)
            from idmtools import __version__
            comps_sim.add_file(
                SimulationFile("idmtools_metadata.json", 'input', description=f'IDMTools {__version__}'),
                data=metadata.encode()
            )

    def refresh_status(self, simulation: Simulation, additional_columns: Optional[List[str]] = None, **kwargs):
        """
        Refresh status of a simulation.

        Args:
            simulation: Simulation to refresh
            additional_columns: Optional additional columns to load from COMPS
            **kwargs:

        Returns:
            None
        """
        cols = ['state']
        if additional_columns:
            cols.extend(additional_columns)
        s = COMPSSimulation.get(id=simulation.uid, query_criteria=QueryCriteria().select(cols))
        simulation.status = convert_comps_status(s.state)

    def to_entity(self, simulation: COMPSSimulation, load_task: bool = False, parent: Optional[Experiment] = None,
                  load_parent: bool = False, load_metadata: bool = False, load_cli_from_workorder: bool = False,
                  **kwargs) -> Simulation:
        """
        Convert COMPS simulation object to IDM Tools simulation object.

        Args:
            simulation: Simulation object
            load_task: Should we load tasks. Defaults to No. This can increase the load items on fetchs
            parent: Optional parent object to prevent reloads
            load_parent: Force load of parent(Beware, This could cause loading loops)
            load_metadata: Should we load metadata by default. If load task is enabled, this is also enabled
            load_cli_from_workorder: Used with COMPS scheduling where the CLI is defined in our workorder
            **kwargs:

        Returns:
            Simulation object
        """
        # Recreate the experiment if needed
        if parent is None or load_parent:
            if logger.isEnabledFor(DEBUG):
                logger.debug(f'Loading parent {simulation.experiment_id}')
            parent = self.platform.get_item(simulation.experiment_id, item_type=ItemType.EXPERIMENT)
        # Get a simulation
        obj = Simulation()
        obj.platform = self.platform
        obj._platform_object = simulation
        obj.parent = parent
        obj.experiment = parent
        # Set its correct attributes
        obj.uid = simulation.id
        obj.tags = simulation.tags
        obj.status = convert_comps_status(simulation.state)
        if simulation.files:
            obj.assets = self.platform._assets.to_entity(simulation.files)

        # should we load metadata
        metadata = self.__load_metadata_from_simulation(obj) if load_metadata else None
        if load_task:
            self._load_task_from_simulation(obj, simulation, metadata)
        else:
            obj.task = None
            self.__extract_cli(simulation, parent, obj, load_cli_from_workorder)

        # call task load options(load configs from files, etc)
        obj.task.reload_from_simulation(obj)
        return obj

    def get_asset_collection_from_comps_simulation(self, simulation: COMPSSimulation) -> Optional[AssetCollection]:
        """
        Get assets from COMPS Simulation.

        Args:
            simulation: Simulation to get assets from

        Returns:
            Simulation Asset Collection, if any.
        """
        if simulation.configuration and simulation.configuration.asset_collection_id:
            return self.platform.get_item(simulation.configuration.asset_collection_id, ItemType.ASSETCOLLECTION)
        return None

    def _load_task_from_simulation(self, simulation: Simulation, comps_sim: COMPSSimulation,
                                   metadata: Dict = None):
        """
        Load task from the simulation object.

        Args:
            simulation: Simulation to populate with task
            comps_sim: Experiment object
            metadata: Metadata loaded to be used in the task object

        Returns:
            None
        """
        simulation.task = None
        if comps_sim.tags and 'task_type' in comps_sim.tags:
            # check for metadata
            if not metadata:
                metadata = self.__load_metadata_from_simulation(simulation)
            try:
                if logger.isEnabledFor(DEBUG):
                    logger.debug(f"Metadata: {metadata}")
                simulation.task = TaskFactory().create(comps_sim.tags['task_type'], **metadata)
            except Exception as e:
                user_logger.warning(f"Could not load task of type {comps_sim.tags['task_type']}. "
                                    f"Received error {str(e)}")
                logger.exception(e)
        # ensure we have loaded the configuration
        if comps_sim.configuration is None:
            comps_sim.refresh(QueryCriteria().select_children('configuration'))

    def __extract_cli(self, comps_sim, parent, simulation, load_cli_from_workorder):
        cli = self._detect_command_line_from_simulation(parent, comps_sim, simulation, load_cli_from_workorder)
        # if we could not find task, set it now, otherwise rebuild the cli
        if simulation.task is None:
            simulation.task = CommandTask(CommandLine.from_string(cli))
        else:
            simulation.task.command = CommandLine.from_string(cli)

    @staticmethod
    def __load_metadata_from_simulation(simulation) -> Dict[str, Any]:
        """
        Load IDMTools metadata from a simulation.

        Args:
            simulation:

        Returns:
            Metadata if found

        Raise:
            FileNotFoundError error if metadata not found
        """
        metadata = None
        for file in simulation.assets:
            if file.filename == "idmtools_metadata.json":
                # load the asset
                metadata = json.loads(file.content.decode('utf-8'))
                return metadata
        raise FileNotFoundError(f"Cannot find idmtools_metadata.json on the simulation {simulation.uid}")

    @staticmethod
    def _detect_command_line_from_simulation(experiment, comps_sim, simulation, load_cli_from_workorder=False):
        """
        Detect Command Line from the Experiment/Simulation objects.

        Args:
            experiment: Experiment object
            comps_sim: Comps sim object
            simulation: Simulation(idmtools) object
            load_cli_from_workorder: Should we load metadata. we use this to determine if we should load our workorder.json

        Returns:
            CommandLine
        Raise:
            ValueError when command cannot be detected
        """
        cli = None
        # do we have a configuration?
        po: COMPSExperiment = experiment.get_platform_object()
        if po.configuration is None:
            po.refresh(QueryCriteria().select_children('configuration'))
        # simulation configuration for executable?
        if comps_sim.configuration and comps_sim.configuration.executable_path:
            cli = f'{comps_sim.configuration.executable_path}'
            if comps_sim.configuration.simulation_input_args:
                cli += " " + comps_sim.configuration.simulation_input_args.strip()
        elif po.configuration and po.configuration.executable_path:
            cli = f'{po.configuration.executable_path} {po.configuration.simulation_input_args.strip()}'
        if cli is None:
            # check if we should try to load our workorder
            if load_cli_from_workorder:
                # filter for workorder
                workorder_obj = None
                for a in simulation.assets:
                    if getattr(a, '_platform_object', None) and isinstance(a._platform_object,
                                                                           SimulationFile) and a._platform_object.file_type == "WorkOrder":
                        workorder_obj = a
                        break
                # if assets
                if workorder_obj:
                    asset: Asset = workorder_obj
                    wo = json.loads(asset.content.decode('utf-8'))
                    cli = wo['Command']
                else:
                    raise ValueError("Could not detect cli")
            else:  # if user doesn't care oabout metadata don't error
                logger.debug(
                    "Could not load the cli from simulation. This is usually due to the use of scheduling config.")
                cli = "WARNING_CouldNotLoadCLI"
        elif logger.isEnabledFor(DEBUG):
            logger.debug(f"Detected task CLI {cli}")
        return cli

    def get_assets(self, simulation: Simulation, files: List[str], include_experiment_assets: bool = True, **kwargs) -> \
            Dict[str, bytearray]:
        """
        Fetch the files associated with a simulation.

        Args:
            simulation: Simulation
            files: List of files to download
            include_experiment_assets: Should we also load experiment assets?
            **kwargs:

        Returns:
            Dictionary of filename -> ByteArray
        """
        # since assets could be in the common assets, we should check that firs
        # load comps config first
        comps_sim: COMPSSimulation = simulation.get_platform_object(load_children=["files", "configuration"])
        if include_experiment_assets and (
                comps_sim.configuration is None or comps_sim.configuration.asset_collection_id is None):
            if logger.isEnabledFor(DEBUG):
                logger.debug("Gathering assets from experiment first")
            exp_assets = get_asset_for_comps_item(self.platform, simulation.experiment, files, self.cache,
                                                  load_children=["configuration"])
            if exp_assets is None:
                exp_assets = dict()
        else:
            exp_assets = dict()
        exp_assets.update(get_asset_for_comps_item(self.platform, simulation, files, self.cache, comps_item=comps_sim))
        return exp_assets

    def list_assets(self, simulation: Simulation, common_assets: bool = False, **kwargs) -> List[Asset]:
        """
        List assets for a simulation.

        Args:
            simulation: Simulation to load data for
            common_assets: Should we load asset files
            **kwargs:

        Returns:
            AssetCollection
        """
        comps_sim: COMPSSimulation = simulation.get_platform_object(load_children=["files", "configuration"])
        assets = []
        # load non comps objects
        if comps_sim.files:
            assets = self.platform._assets.to_entity(comps_sim.files).assets

        if common_assets:
            # here we are loading the simulation assets
            sa = self.get_asset_collection_from_comps_simulation(comps_sim)
            if sa:
                assets.extend(sa.assets)
        return assets

    def retrieve_output_files(self, simulation: Simulation):
        """
        Retrieve the output files for a simulation.

        Args:
            simulation: Simulation to fetch files for

        Returns:
            List of output files for simulation
        """
        metadata = simulation.get_platform_object().retrieve_output_file_info([])
        assets = self.platform._assets.to_entity(metadata).assets
        return assets

    def all_files(self, simulation: Simulation, common_assets: bool = False, outfiles: bool = True, **kwargs) -> List[Asset]:
        """
        Returns all files for a specific simulation including experiments or non-assets.

        Args:
            simulation: Simulation all files
            common_assets: Include experiment assets
            outfiles: Include output files
            **kwargs:

        Returns:
            AssetCollection
        """
        ac = AssetCollection()
        ac.add_assets(self.list_assets(simulation, **kwargs))
        if common_assets:
            ac.add_assets(simulation.parent.assets)
        if outfiles:
            ac.add_assets(self.retrieve_output_files(simulation))

        return ac.assets

    def create_sim_directory_map(self, simulation_id: str) -> Dict:
        """
        Build simulation working directory mapping.
        Args:
            simulation_id: simulation id

        Returns:
            Dict of simulation id as key and working dir as value
        """
        from idmtools_platform_comps.utils.linux_mounts import set_linux_mounts, clear_linux_mounts
        set_linux_mounts(self.platform)
        comps_sim = self.platform.get_item(simulation_id, ItemType.SIMULATION,
                                           query_criteria=QueryCriteria().select(['id', 'state']).select_children(
                                               'hpc_jobs'), raw=True)
        sim_map = {str(comps_sim.id): comps_sim.hpc_jobs[-1].working_directory}
        clear_linux_mounts(self.platform)
        return sim_map
