import json
import logging
import ntpath
import os


from COMPS import Client
from COMPS.Data import AssetCollection, AssetCollectionFile, Configuration, Experiment as COMPSExperiment, \
    QueryCriteria, Simulation as COMPSSimulation, SimulationFile
from COMPS.Data.Simulation import SimulationState
from dataclasses import dataclass, field

from idmtools.core import CacheEnabled, TypeVar, typing
from idmtools.core.experiment_factory import experiment_factory
from idmtools.core.enums import EntityStatus
from idmtools.entities import IPlatform, ISuite
from idmtools.entities.ianalyzer import TAnalyzerList
from idmtools.entities.iexperiment import TExperiment, TExperimentList, IExperiment
from idmtools.entities.iitem import TItemList, TItem
from idmtools.entities.isimulation import TSimulationList, ISimulation
from idmtools.utils.time import timestamp
from typing import NoReturn
import uuid

logging.getLogger('COMPS.Data.Simulation').disabled = True
logger = logging.getLogger(__name__)


class COMPSPriority:
    Lowest = "Lowest"
    BelowNormal = "BelowNormal"
    Normal = "Normal"
    AboveNormal = "AboveNormal"
    Highest = "Highest"


@dataclass
class COMPSPlatform(IPlatform, CacheEnabled):
    """
    Represents the platform allowing to run simulations on COMPS.
    """

    MAX_SUBDIRECTORY_LENGTH = 35  # avoid maxpath issues on COMPS

    endpoint: str = field(default="https://comps2.idmod.org")
    environment: str = field(default="Bayesian")
    priority: str = field(default=COMPSPriority.Lowest)
    simulation_root: str = field(default="$COMPS_PATH(USER)\\output")
    node_group: str = field(default="emod_abcd")
    num_retires: int = field(default=0)
    num_cores: int = field(default=1)
    exclusive: bool = field(default=False)

    # Private fields
    _comps_experiment: 'COMPSExperiment' = field(default=None, init=False, compare=False)
    _comps_experiment_id: 'uuid' = field(default=None, init=False, compare=False)

    def __post_init__(self):
        super().__post_init__()
        print("\nUser Login:")
        print(json.dumps({"endpoint": self.endpoint, "environment": self.environment}, indent=3))
        self._login()

    def _login(self):
        try:
            Client.auth_manager()
        except RuntimeError:
            Client.login(self.endpoint)

    @property
    def comps_experiment(self):
        if self._comps_experiment and self._comps_experiment.id == self._comps_experiment_id:
            return self._comps_experiment

        self._login()
        self._comps_experiment = COMPSExperiment.get(id=self._comps_experiment_id,
                                                     query_criteria=QueryCriteria().select(["id"]).select_children(
                                                         ["tags"]))
        return self._comps_experiment

    @comps_experiment.setter
    def comps_experiment(self, comps_experiment):
        self._comps_experiment = comps_experiment
        self._comps_experiment_id = comps_experiment.id

    def send_assets(self, item, **kwargs) -> NoReturn:
        # TODO: add asset sending for suites if needed
        if isinstance(item, ISimulation):
            self._send_assets_for_simulation(simulation=item, **kwargs)
        elif isinstance(item, IExperiment):
            self._send_assets_for_experiment(experiment=item, **kwargs)
        else:
            raise Exception(f'Unknown how to send assets for item type: {type(item)} '
                            f'for platform: {self.__class__.__name__}')

    @staticmethod
    def _send_assets_for_experiment(experiment: TExperiment, **kwargs) -> NoReturn:

        if experiment.assets.count == 0:
            return

        ac = AssetCollection()
        for asset in experiment.assets:
            ac.add_asset(AssetCollectionFile(file_name=asset.filename, relative_path=asset.relative_path),
                         data=asset.content)
        ac.save()
        experiment.assets.uid = ac.id
        print("Asset collection for experiment: {}".format(ac.id))

    @staticmethod
    def _send_assets_for_simulation(simulation, comps_simulation) -> NoReturn:
        for asset in simulation.assets:
            comps_simulation.add_file(simulationfile=SimulationFile(asset.filename, 'input'), data=asset.content)

    @staticmethod
    def _clean_experiment_name(experiment_name: str) -> str:
        """
        Enforce any COMPS-specific demands on experiment names.
        Args:
            experiment_name: name of the experiment
        Returns: the experiment name allowed for use
        """
        for c in ['/', '\\', ':']:
            experiment_name = experiment_name.replace(c, '_')
        return experiment_name

    def _create_experiment(self, experiment: TExperiment) -> uuid:
        self._login()

        # Cleanup the name
        experiment_name = COMPSPlatform._clean_experiment_name(experiment.name)

        # Define the subdirectory
        subdirectory = experiment_name[0:self.MAX_SUBDIRECTORY_LENGTH] + '_' + timestamp()

        config = Configuration(
            environment_name=self.environment,
            simulation_input_args=experiment.command.arguments + " " + experiment.command.options,
            working_directory_root=os.path.join(self.simulation_root, subdirectory),
            executable_path=experiment.command.executable,
            node_group_name=self.node_group,
            maximum_number_of_retries=self.num_retires,
            priority=self.priority,
            min_cores=self.num_cores,
            max_cores=self.num_cores,
            exclusive=self.exclusive
        )

        e = COMPSExperiment(name=experiment_name,
                            configuration=config,
                            suite_id=experiment.suite_id)

        # Add tags if present
        if experiment.tags:
            e.set_tags(experiment.tags)

        # Save the experiment
        e.save()
        self.comps_experiment = e

        experiment.uid = e.id
        self.send_assets(item=experiment)
        return experiment.uid


    def create_items(self, items: TItemList) -> 'List[uuid]':
        # TODO: add ability to create suites
        types = list({type(item) for item in items})
        if len(types) != 1:
            raise Exception('create_items only works with items of a single type at a time.')
        sample_item = items[0]
        if isinstance(sample_item, ISimulation):
            ids = self._create_simulations(simulation_batch=items)
        elif isinstance(sample_item, IExperiment):
            ids = [self._create_experiment(experiment=item) for item in items]
        else:
            raise Exception(f'Unable to create items of type: {type(sample_item)} '
                            f'for platform: {self.__class__.__name__}')
        for item in items:
            item.platform = self
        return ids

    def _create_simulations(self, simulation_batch: 'TSimulationList') -> 'List[uuid]':
        self._login()
        created_simulations = []

        for simulation in simulation_batch:
            s = COMPSSimulation(name=simulation.experiment.name, experiment_id=simulation.experiment.uid,
                                configuration=Configuration(asset_collection_id=simulation.experiment.assets.uid))

            self.send_assets(item=simulation, comps_simulation=s)
            s.set_tags(simulation.tags)
            created_simulations.append(s)

        COMPSSimulation.save_all(None, save_semaphore=COMPSSimulation.get_save_semaphore())

        # Register the IDs
        return [s.id for s in created_simulations]

    def run_items(self, items: TItemList) -> NoReturn:
        # TODO: add ability to run experiments and suites
        for item in items:
            try:
                self._run_simulations_for_experiment(experiment=item)
            except:
                raise Exception(f'Unable to run item id: {item.uid} of type: {type(item)} ')
        for item in items:
            item.platform = self

    def _run_simulations_for_experiment(self, experiment: 'TExperiment') -> NoReturn:
        self._login()
        self._comps_experiment_id = experiment.uid
        self.comps_experiment.commission()

    @staticmethod
    def _convert_COMPS_status(comps_status):
        if comps_status == SimulationState.Succeeded:
            return EntityStatus.SUCCEEDED
        elif comps_status in (SimulationState.Canceled, SimulationState.CancelRequested, SimulationState.Failed):
            return EntityStatus.FAILED
        elif comps_status == SimulationState.Created:
            return EntityStatus.CREATED
        else:
            return EntityStatus.RUNNING

    def refresh_status(self, item: TItem) -> NoReturn:
        if isinstance(item, ISimulation):
            raise Exception(f'Unknown how to refresh items of type {type(item)} '
                            f'for platform: {self.__class__.__name__}')
        elif isinstance(item, IExperiment):
            return_value = self._refresh_experiment_status(experiment=item)
        elif isinstance(item, ISuite):
            raise Exception(f'Unknown how to refresh items of type {type(item)} '
                            f'for platform: {self.__class__.__name__}')
        item.platform = self
        return return_value

    def _refresh_experiment_status(self, experiment: TExperiment) -> NoReturn:
        # Do nothing if we are already done
        if experiment.done:
            return

        self._comps_experiment_id = experiment.uid
        self._login()

        comps_simulations = self.comps_experiment.get_simulations(
            query_criteria=QueryCriteria().select(["id", "state"]))

        for s in experiment.children(refresh=True):
            if s.done:
                continue

            for comps_simulation in comps_simulations:
                if comps_simulation.id == s.uid:
                    s.status = COMPSPlatform._convert_COMPS_status(comps_simulation.state)
                    break

    def _retrieve_experiments(self, suite: 'TSuite') -> TExperimentList:
        raise NotImplementedError('No method for retrieving experiments for a suite object implemented yet.')
        return experiments

    def _retrieve_simulations(self, experiment: TExperiment) -> TSimulationList:
        self._comps_experiment_id = experiment.uid

        simulations = []
        for s in self.comps_experiment.get_simulations(
                query_criteria=QueryCriteria().select(["id", "state"]).select_children(["tags"])):
            sim = experiment.simulation()
            sim.uid = s.id
            sim.tags = s.tags
            sim.status = COMPSPlatform._convert_COMPS_status(s.state)
            simulations.append(sim)
        return simulations

    # TODO: try to get rid of blanket except clauses
    # TODO: verify the retrieve methods called here actually error when they fail to retrieve anything
    def get_children(self, item: TItem) -> TItemList:
        children = None
        successful = False
        try:
            children = self._retrieve_experiments(suite=item)
            successful = True
        except:
            pass
        if not successful:
            try:
                children = self._retrieve_simulations(experiment=item)
                successful = True
            except:
                pass
        if not successful:
            raise self.UnknownItemException(f'Unable to retrieve children for unknown item '
                                            f'id: {item.uid} of type: {type(item)}')
        for child in children:
            child.platform = self
        return children

    # TODO: This method is a total hack for now. It doesn't actually look for and attach ALL experiments for the suite
    # as it needs to.
    def _retrieve_suite(self, suite_id: uuid) -> 'TSuite':
        raise NotImplementedError('Method for retrieving a suite by id is not complete')
        # from idmtools_models.dtk.DTKSuite import DTKSuite
        # experiments = [experiment]
        # suite = DTKSuite(experiments=experiments)
        # suite.children = experiments
        # suite.parent = None
        # return suite

    def _retrieve_experiment(self, experiment_id: uuid) -> TExperiment:
        self._comps_experiment_id = experiment_id
        experiment = experiment_factory.create(key=self.comps_experiment.tags.get('type', None),
                                               tags=self.comps_experiment.tags)
        experiment.platform = self
        experiment.uid = self.comps_experiment.id
        return experiment

    # @retry_function
    def _retrieve_simulation(self, simulation_id: 'uuid') -> 'TSimulation':
        raise NotImplementedError('Method for retrieving a simulation by id is not complete')
        # simulation = COMPSSimulation.get(id=simulation_id)
        # return simulation

    # TODO: verify the retrieve methods called here actually error when they fail to retrieve anything
    def get_parent(self, item: TItem) -> TItem:
        parent = None
        successful = False
        try:
            parent = self._retrieve_suite(suite_id=item.parent_id)
            successful = True
        except NotImplementedError:  # TODO: temporary for development debugging ONLY (breaks some functionality). We need to implement retrieve_suite rather than kludge this eventually.
            parent = None
            successful = True
        if not successful:
            try:
                parent = self._retrieve_experiment(experiment_id=item.parent_id)
                successful = True
            except:
                pass
        if not successful:
            raise self.UnknownItemException(f'Unable to retrieve parent for unknown item '
                                            f'id: {item.uid} of type: {type(item)}')
        parent.platform = self
        return parent

    @staticmethod
    def _get_file_for_collection(collection_id: uuid, file_path: str) -> NoReturn:
        print(f"Cache miss for {collection_id} {file_path}")

        # retrieve the collection
        ac = AssetCollection.get(collection_id, QueryCriteria().select_children('assets'))

        # Look for the asset file in the collection
        file_name = ntpath.basename(file_path)
        path = ntpath.dirname(file_path).lstrip(f"Assets\\")

        for asset_file in ac.assets:
            if asset_file.file_name == file_name and (asset_file.relative_path or '') == path:
                return asset_file.retrieve()

    def get_files(self, item: TItem, files: typing.List[str]) -> dict:
        self._login()

        # Retrieve the simulation from COMPS
        comps_simulation = COMPSSimulation.get(item.uid,
                                               query_criteria=QueryCriteria().select(['id']).select_children(
                                                   ["files", "configuration"]))

        # Separate the output files in 2 groups:
        # - one for the transient files (retrieved through the comps simulation)
        # - one for the asset collection files (retrieved through the asset collection)
        all_paths = set(files)
        assets = set(path for path in all_paths if path.lower().startswith("assets"))
        transients = all_paths.difference(assets)

        # Create the return dict
        ret = {}

        # Retrieve the transient if any
        if transients:
            transient_files = comps_simulation.retrieve_output_files(paths=transients)
            ret = dict(zip(transients, transient_files))

        # Take care of the assets
        if assets:
            # Get the collection_id for the simulation
            collection_id = comps_simulation.configuration.asset_collection_id

            # Retrieve the files
            for file_path in assets:
                # Normalize the separators
                normalized_path = ntpath.normpath(file_path)
                ret[file_path] = self.cache.memoize()(self._get_file_for_collection)(collection_id, normalized_path)

        return ret

    # TODO move into analyze manager?
    def initialize_for_analysis(self, items: TItemList, analyzers: TAnalyzerList) -> NoReturn:
        # run any necessary analysis prep steps on groups of items (hierarchy level > 0)
        for analyzer in analyzers:
            analyzer.per_group(items=items)

    def get_item(self, id: uuid) -> TItem:
        # TODO: no options currently for loading a simulation or suite directly yet
        successful = False
        if not successful:
            try:
                item = self._retrieve_suite(suite_id=id)
                successful = True
            except:
                pass
        if not successful:
            try:
                item = self._retrieve_experiment(experiment_id=id)
                successful = True
            except:
                pass
        if not successful:
            try:
                item = self._retrieve_simulation(simulation_id=id)
                successful = True
            except:
                pass
        if not successful:
            raise self.UnknownItemException(f'Unable to load item id: {id} from platform: {self.__class__.__name__}')

        item.platform = self
        return item

    #
    # platform-specific convenience methods for dealing with domain-specific terminology.
    # possibly move out to a multi-inherited interface (for internal IDM platforms)
    #

    # def get_simulation(self, sim_id: 'uuid') -> Any:
    #     return self.get_item(id=sim_id, level=0)
    #
    # def get_experiment(self, exp_id: 'uuid') -> 'TExperiment':
    #     return self.get_item(id=exp_id, level=1)
    #
    # def get_suite(self, suite_id: 'uuid') -> Any:
    #     return self.get_item(id=suite_id, level=2)

    # def get_simulations_in_experiment(self, experiment: 'TExperiment') -> 'TSimulationList':
    #     return self.get_objects_by_relationship(object=experiment, relationship=self.CHILD)
    #
    # def get_experiments_in_suite(self, suite) -> 'List[TExperiment]':
    #     return self.get_objects_by_relationship(object=suite, relationship=self.CHILD)
    #
    # def get_experiment_for_simulation(self, simulation: 'TSimulation') -> 'TExperiment':
    #     return self.get_objects_by_relationship(object=simulation, relationship=self.PARENT)[0]
    #
    # def get_suite_for_experiment(self, experiment: 'TExperiment') -> Any:
    #     return self.get_objects_by_relationship(object=experiment, relationship=self.PARENT)
