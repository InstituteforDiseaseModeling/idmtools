import dataclasses
import functools
import logging
import os
from collections import defaultdict
from logging import getLogger
from typing import Optional, NoReturn, Union, List, Dict
from dataclasses import dataclass
from pathlib import Path
import uuid
from docker.models.containers import Container
from idmtools.assets import Asset
from idmtools.core import UnknownItemException
from idmtools.entities import IExperiment, IPlatform
from idmtools.entities.ianalyzer import TAnalyzerList
from idmtools.entities.iitem import TItemList, TItem
from idmtools_platform_local import __version__
from idmtools.entities.iexperiment import TExperiment
from idmtools.entities.isimulation import TSimulation, ISimulation
from idmtools_platform_local.client.experiments_client import ExperimentsClient
from idmtools_platform_local.client.simulations_client import SimulationsClient
from idmtools_platform_local.docker.docker_operations import DockerOperations
from idmtools_platform_local.workers.brokers import setup_broker
from idmtools.core.experiment_factory import experiment_factory

status_translate = dict(
    created='CREATED',
    in_progress='RUNNING',
    canceled='canceled',
    failed='FAILED',
    done='SUCCEEDED'
)


def local_status_to_common(status):
    from idmtools.core import EntityStatus
    return EntityStatus[status_translate[status]]


logger = getLogger(__name__)
docker_repo = f'{os.getenv("DOCKER_REPO", "idm-docker-public")}.packages.idmod.org'


@dataclass
class LocalPlatform(IPlatform):
    host_data_directory: str = os.path.join(str(Path.home()), '.local_data')
    network: str = 'idmtools'
    redis_image: str = 'redis:5.0.4-alpine'
    redis_port: int = 6379
    runtime: Optional[str] = None
    redis_mem_limit: str = '128m'
    redis_mem_reservation: str = '64m'
    postgres_image: str = 'postgres:11.4'
    postgres_mem_limit: str = '64m'
    postgres_mem_reservation: str = '32m'
    postgres_port: Optional[str] = 5432
    workers_image: str = f'{docker_repo}/idmtools_local_workers:{__version__.replace("+", ".")}'
    workers_ui_port: int = 5000
    default_timeout: int = 30
    run_as: Optional[str] = None
    # We use this to manage our docker containers
    _docker_operations: Optional[DockerOperations] = dataclasses.field(default=None, metadata={"pickle_ignore": True})

    def __post_init__(self):
        super().__post_init__()
        # ensure our brokers are started
        setup_broker()
        if self._docker_operations is None:
            # extract configuration details for the docker manager
            local_docker_options = [f.name for f in dataclasses.fields(DockerOperations)]
            opts = {k: v for k, v in self.__dict__.items() if k in local_docker_options}
            self._docker_operations = DockerOperations(**opts)
            # start the services
            self._docker_operations.create_services()

    """
    Represents the platform allowing to run simulations locally.
    """

    def create_items(self, items: 'TItem') -> 'List[uuid]':
        """
        Create items on the local Platform. Items must all be the same type.
        Args:
            items: List of items to be created

        Returns:
            List of id of created items
        """
        types = list({type(item) for item in items})
        if len(types) != 1:
            raise Exception('create_items only works with items of a single type at a time.')
        sample_item = items[0]
        if isinstance(sample_item, ISimulation):
            ids = self._create_simulations(simulations_batch=items)
        elif isinstance(sample_item, IExperiment):
            ids = [self._create_experiment(experiment=item) for item in items]
        else:
            raise Exception(f'Unable to create items of type: {type(sample_item)} '
                            f'for platform: {self.__class__.__name__}')
        for item in items:
            item.platform = self
        return ids

    def run_items(self, items: TItemList) -> NoReturn:
        """
        Execute the specified items

        Args:
            items: List of items to execute

        Returns:
            None
        """
        for item in items:
            try:
                self._run_simulations(experiment=item)
            except:
                raise Exception(f'Unable to run item id: {item.uid} of type: {type(item)} ')
        for item in items:
            item.platform = self

    def send_assets(self, item: TItem, **kwargs) -> NoReturn:
        """
        Send assets for item to platform
        Args:
            item:
            **kwargs:

        Returns:

        """
        if isinstance(item, ISimulation):
            self._send_assets_for_simulation(item, **kwargs)
        elif isinstance(item, IExperiment):
            self._send_assets_for_experiment(item, **kwargs)
        else:
            raise Exception(f'Unknown how to send assets for item type: {type(item)} '
                            f'for platform: {self.__class__.__name__}')

    def refresh_status(self, item) -> NoReturn:
        """
        Refresh the status of the specified item

        Args:
            item: Item to refresh status of

        Returns:

        """
        if isinstance(item, ISimulation):
            raise Exception(f'Unknown how to refresh items of type {type(item)} '
                            f'for platform: {self.__class__.__name__}')
        elif isinstance(item, IExperiment):
            return_value = self._refresh_experiment_status(experiment=item)
        else:
            raise Exception(f'Cannot fetch status of items of type {type(item)}')
        item.platform = self
        return return_value

    def get_item(self, id: 'uuid') -> Union[ISimulation, IExperiment]:
        """
        Return the specified item from the platform

        Args:
            id: id of item to fetch

        Returns:
            Either the experiment or simulation matching the id
        """
        item = None
        for lookup in [self._retrieve_simulation, self._retrieve_experiment]:
            try:
                item = lookup(id)
                break
            # TODO - Once _retrieve_simulation it implemented, remove NotImplementedError
            except (FileNotFoundError, NotImplementedError) as e:
                logger.debug(e)
                pass
        if item is None:
            raise UnknownItemException(f'Unable to load item id: {id} from platform: {self.__class__.__name__}')
        item.platform = self
        return item

    def get_parent(self, item: 'TItem') -> IExperiment:
        """
        Returns the parent of the item. On Local Platform, only simulations have parents so this will only work
        on ISimulations objects. The return will always be an IExperiment object

        Args:
            item: Item to load parent of

        Returns:
            Experiment which is the parent of item
        """
        if isinstance(item, IExperiment):
            raise ValueError("LocalPlatform Experiments have no parents")

        parent = self._retrieve_experiment(item.parent_id)
        parent.platform = self
        return parent

    def get_children(self, item: 'TItem') -> List[ISimulation]:
        """
        Returns the children for given object. On the local platform, only Experiments have children so item
        should be an Experiment. The return will always be a list of simulations

        Args:
            item: item to load children for

        Returns:
            List of simulations that are the children of item
        """
        if not isinstance(item, IExperiment):
            raise ValueError("Only Experiments have no children on the LocalPlatform")

        children = self._retrieve_simulations(item)
        for child in children:
            child.platform = self
        return children

    def get_files(self, item: 'TItem', files: 'List[str]') -> 'Dict[str, bytearray]':
        """
        Returns a dictionary of the specified files for the specified item.

        Args:
            item: Item to fetch files for
            files: List of file names to fetch

        Returns:
            A dict container filename->bytearray
        """
        if not isinstance(item, ISimulation):
            raise NotImplementedError("Retrieving files only implemented for Simulations at the moment")

        return self._get_assets_for_simulation(item, files)

    def initialize_for_analysis(self, items: 'TItemList', analyzers: TAnalyzerList) -> NoReturn:
        # run any necessary analysis prep steps on groups of items (hierarchy level > 0)
        for analyzer in analyzers:
            analyzer.per_group(items=items)

    def _retrieve_simulation(self, simulation_id: 'uuid') -> 'TSimulation':
        """
        Retrieve a simulation object by id

        Args:
            simulation_id: id of simulation to retrieve

        Returns:
            Simulation matching sim id
        """
        raise NotImplementedError('Method for retrieving a simulation by id is not complete')

    def _retrieve_experiment(self, experiment_id: str) -> IExperiment:
        """
        Restore experiment from local platform

        Args:
            experiment_id: Id of experiment to restore

        Returns:

        """
        experiment_dict = ExperimentsClient.get_one(experiment_id)
        experiment = experiment_factory.create(experiment_dict['tags'].get("type"), tags=experiment_dict['tags'])
        experiment.uid = experiment_dict['experiment_id']
        return experiment

    def _get_assets_for_simulation(self, simulation: TSimulation, output_files) -> Dict[str, bytearray]:  # noqa: F821
        """
        Get assets for a specific simulation

        Args:
            simulation: Simulation object to fetch files for
            output_files: List of files to fetch

        Returns:
            Returns a dict containing mapping of filename->bytearry
        """
        all_paths = set(output_files)

        assets = set(path for path in all_paths if path.lower().startswith("assets"))
        transients = all_paths.difference(assets)

        # Create the return dict
        ret = {}

        # Retrieve the transient if any
        if transients:
            sim_path = f'{simulation.experiment.uid}/{simulation.uid}'
            transients_files = self.retrieve_output_files(job_id_path=sim_path, paths=transients)
            ret = dict(zip(transients, transients_files))

        # Take care of the assets
        if assets:
            asset_path = f'{simulation.experiment.uid}'
            common_files = self.retrieve_output_files(job_id_path=asset_path, paths=assets)
            ret.update(dict(zip(assets, common_files)))

        return ret

    def restore_simulations(self, experiment: TExperiment):  # noqa: F821
        """
        Restores the simulation for a specific experiment

        Args:
            experiment: Experiment to retore simulations for

        Returns:

        """
        simulation_dict = SimulationsClient.get_all(experiment_id=experiment.uid)

        for sim_info in simulation_dict:
            sim = experiment.simulation()
            sim.uid = sim_info['simulation_uid']
            sim.tags = sim_info['tags']
            sim.status = local_status_to_common(sim_info['status'])
            experiment.simulations.append(sim)

    def _refresh_experiment_status(self, experiment: TExperiment, update_sim_status=True):  # noqa: F821
        """

        Args:
            experiment:

        Returns:

        """
        # Update the status of simulations objects within experiment
        if update_sim_status:
            status = SimulationsClient.get_all(experiment_id=experiment.uid, per_page=99999)
            for s in experiment.simulations:
                sim_status = [st for st in status if st['simulation_uid'] == s.uid]

                if sim_status:
                    s.status = local_status_to_common(sim_status[0]['status'])
        return experiment

    def _create_experiment(self, experiment: IExperiment):
        """
        Creates the experiment object on the LocalPlatform
        Args:
            experiment: Experiment object to create

        Returns:
            Id
        """
        from idmtools_platform_local.tasks.create_experiment import CreateExperimentTask

        m = CreateExperimentTask.send(experiment.tags, experiment.simulation_type)
        eid = m.get_result(block=True, timeout=self.default_timeout * 1000)
        experiment.uid = eid
        path = "/".join(["/data", experiment.uid, "Assets"])
        self._docker_operations.create_directory(path)
        self._send_assets_for_experiment(experiment)
        return experiment.uid

    def _send_assets_for_experiment(self, experiment):
        """
        Sends assets for specified experiment

        Args:
            experiment: Experiment to send assets for

        Returns:
            None
        """
        # Go through all the assets
        path = "/".join(["/data", experiment.uid, "Assets"])
        worker = self._docker_operations.get_workers()
        list(map(functools.partial(self.send_asset_to_docker, path=path, worker=worker), experiment.assets))

    def _send_assets_for_simulation(self, simulation, worker: Container = None):
        """
        Send assets for specified simulation

        Args:
            simulation: Simulation Id
            worker: Options worker container. Useful in batches to reduce overhead

        Returns:
            None
        """
        # Go through all the assets
        path = "/".join(["/data", simulation.experiment.uid, simulation.uid])
        if worker is None:
            worker = self._docker_operations.get_workers()

        items = self.assets_to_copy_multiple_list(path, simulation.assests)
        self._docker_operations.copy_multiple_to_container(worker, items)

    def assets_to_copy_multiple_list(self, path, assets):
        """
        Batch copies a set of items assets to a grouped by path
        Args:
            path: Target path
            assets: Assets to copy

        Returns:
            Dict of items groups be path.
        """
        items = defaultdict(list)
        for asset in assets:
            file_path = asset.absolute_path
            remote_path = "/".join([path, asset.relative_path]) if asset.relative_path else path
            self._docker_operations.create_directory(remote_path)
            items[remote_path].append(
                (file_path if file_path else asset.content, asset.filename if not file_path else None))
        return items

    def send_asset_to_docker(self, asset: Asset, path: str, worker: Container = None) -> NoReturn:
        """
        Handles sending an asset to docker.

        Args:
            asset: Asset object to send
            path: Path to send find to within docker container
            worker: Optional worker to reduce docker calls

        Returns:
            (NoReturn): Nada
        """
        file_path = asset.absolute_path
        remote_path = "/".join([path, asset.relative_path]) if asset.relative_path else path
        # ensure remote directory exists
        result = self._docker_operations.create_directory(remote_path)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Creating directory {remote_path} result: {str(result)}")
        # is it a real file?
        if worker is None:
            worker = self._docker_operations.get_workers()
        self._docker_operations.copy_to_container(worker, file_path if file_path else asset.content, remote_path,
                                                  asset.filename if not file_path else None)

    def _create_simulations(self, simulations_batch: List[ISimulation]):
        """
        Create a set of simulations

        Args:
            simulations_batch: List of simulations to create

        Returns:
            Ids of simulations created
        """
        from idmtools_platform_local.tasks.create_simulation import CreateSimulationsTask

        worker = self._docker_operations.get_workers()

        m = CreateSimulationsTask.send(simulations_batch[0].experiment.uid, [s.tags for s in simulations_batch])
        ids = m.get_result(block=True, timeout=self.default_timeout * 1000)

        items = dict()
        # update our uids and then build a list of files to copy
        for i, simulation in enumerate(simulations_batch):
            simulation.uid = ids[i]
            path = "/".join(["/data", simulation.experiment.uid, simulation.uid])
            items.update(self.assets_to_copy_multiple_list(path, simulation.assets))
        result = self._docker_operations.copy_multiple_to_container(worker, items)
        if not result:
            raise IOError("Coping of data for simulations failed.")
        return ids

    def _run_simulations(self, experiment: IExperiment):
        """
        Run a specified experiment's simulations

        Args:
            experiment: Experiment who's simulations should be ran

        Returns:
            None
        """
        from idmtools_platform_local.tasks.run import RunTask
        for simulation in experiment.simulations:
            RunTask.send(simulation.experiment.command.cmd, simulation.experiment.uid, simulation.uid)

    def retrieve_output_files(self, job_id_path, paths):
        """
        Retrieves output files
        Args:
            job_id_path: For experiments, this should just be the id. For simulations, the path should be
            experiment_id/simulation id
            paths:

        Returns:

        """

        byte_arrs = []

        for path in paths:
            full_path = os.path.join(self.host_data_directory, 'workers', job_id_path, path)
            with open(full_path, 'rb') as fin:
                byte_arrs.append(fin.read())
        return byte_arrs

    def _retrieve_simulations(self, item):
        raise NotImplementedError('Method for retrieving a simulations not completed')
