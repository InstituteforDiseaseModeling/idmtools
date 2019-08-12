import logging
import ntpath
import os
import typing

from COMPS import Client
from COMPS.Data import AssetCollection, AssetCollectionFile, Configuration, Experiment as COMPSExperiment, \
    QueryCriteria, Simulation as COMPSSimulation, SimulationFile
from COMPS.Data.Simulation import SimulationState
from dataclasses import dataclass, field

from idmtools.core import CacheEnabled
from idmtools.core.enums import EntityStatus
from idmtools.core.ExperimentFactory import experiment_factory
from idmtools.core.item_id import ItemId
from idmtools.entities import IPlatform
from idmtools.utils.time import timestamp
from typing import Any, List, NoReturn

if typing.TYPE_CHECKING:
    from idmtools.core.types import TAnalyzerList, TExperiment, TItem, TItemList, TSimulation, TSimulationList
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

    def send_assets(self, object, **kwargs) -> NoReturn:
        level = object.level
        if level == 0:
            self._send_assets_for_simulation(simulation=object, **kwargs)
        elif level == 1:
            self._send_assets_for_experiment(experiment=object, **kwargs)
        elif level == 2:
            raise Exception(f'Unknown how to send assets for object level: {level} '
                            f'for platform: {self.__class__.__name__}')
        else:
            raise Exception(f'Unknown object level: {level} for platform: {self.__class__.__name__}')

    @staticmethod
    def _send_assets_for_experiment(experiment: 'TExperiment', **kwargs) -> NoReturn:
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
    def _clean_experiment_name(experiment_name: 'str') -> 'str':
        """
        Enforce any COMPS-specific demands on experiment names.
        Args:
            experiment_name: name of the experiment
        Returns: the experiment name allowed for use
        """
        for c in ['/', '\\', ':']:
            experiment_name = experiment_name.replace(c, '_')
        return experiment_name

    def _create_experiment(self, experiment: 'TExperiment') -> 'uuid':
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
        self.send_assets(object=experiment)
        return experiment.uid

    def create_objects(self, objects) -> 'List[uuid]':
        levels = list({object.level for object in objects})
        if len(levels) != 1:
            raise Exception('create_objects only works with objects of a single level at a time.')
        level = levels[0]
        if level == 0:
            ids = self._create_simulations(simulation_batch=objects)
        elif level == 1:
            ids = [self._create_experiment(experiment=object) for object in objects]
        elif level == 2:
            raise Exception(f'Unknown how to create objects for hierarchy level {level} '
                            f'for platform: {self.__class__.__name__}')
        else:
            raise Exception(f'Unknown level: {level} for platform: {self.__class__.__name__}')
        return ids

    def _create_simulations(self, simulation_batch: 'TSimulationList') -> 'List[uuid]':
        self._login()
        created_simulations = []

        for simulation in simulation_batch:
            s = COMPSSimulation(name=simulation.experiment.name, experiment_id=simulation.experiment.uid,
                                configuration=Configuration(asset_collection_id=simulation.experiment.assets.uid))

            self.send_assets(object=simulation, comps_simulation=s)
            s.set_tags(simulation.tags)
            created_simulations.append(s)

        COMPSSimulation.save_all(None, save_semaphore=COMPSSimulation.get_save_semaphore())

        # Register the IDs
        return [s.id for s in created_simulations]

    def run_objects(self, objects) -> NoReturn:
        for object in objects:
            level = object.level
            if level == 0:
                raise Exception(f'Unknown how to run objects for hierarchy level {object.level} '
                                f'for platform: {self.__class__.__name__}')

            elif level == 1:
                self._run_simulations(experiment=object)
            elif level == 2:
                raise Exception(f'Unknown how to refresh objects for hierarchy level {object.level} '
                                f'for platform: {self.__class__.__name__}')
            else:
                raise Exception(f'Unknown object hierarchy level {level} for platform: {self.__class__.__name__}')

    def _run_simulations(self, experiment: 'TExperiment') -> NoReturn:
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

    def refresh_status(self, object) -> NoReturn:
        if object.level == 0:
            raise Exception(f'Unknown how to refresh objects for hierarchy level {object.level} '
                            f'for platform: {self.__class__.__name__}')
        elif object.level == 1:
            return self._refresh_experiment_status(experiment=object)
        elif object.level == 2:
            raise Exception(f'Unknown how to refresh objects for hierarchy level {object.level} '
                            f'for platform: {self.__class__.__name__}')
        else:
            raise Exception(f'Unknown object hierarchy level {level} for platform: {self.__class__.__name__}')

    def _refresh_experiment_status(self, experiment) -> NoReturn:
        # Do nothing if we are already done
        if experiment.done:
            return

        self._comps_experiment_id = experiment.uid
        self._login()

        comps_simulations = self.comps_experiment.get_simulations(
            query_criteria=QueryCriteria().select(["id", "state"]))

        for s in experiment.simulations:
            if s.done:
                continue

            for comps_simulation in comps_simulations:
                if comps_simulation.id == s.uid:
                    s.status = COMPSPlatform._convert_COMPS_status(comps_simulation.state)
                    break

    def _retrieve_simulations(self, experiment: 'TExperiment') -> 'TSimulationList':
        self._comps_experiment_id = experiment.uid

        simulations = []
        for s in self.comps_experiment.get_simulations(
                query_criteria=QueryCriteria().select(["id", "state"]).select_children(["tags"])):
            sim = experiment.simulation()
            sim.uid = s.id
            sim.tags = s.tags
            sim.status = COMPSPlatform._convert_COMPS_status(s.state)
            hierarchy = [('simulation_id', sim.uid),
                         ('experiment_id', experiment.uid),
                         ('suite_id', experiment.suite_id)]
            sim.full_id = ItemId(group_tuples=hierarchy)
            simulations.append(sim)
        return simulations

    def _retrieve_experiment(self, experiment_id: 'uuid') -> 'TExperiment':
        self._comps_experiment_id = experiment_id
        experiment = experiment_factory.create(self.comps_experiment.tags.get("type"), tags=self.comps_experiment.tags)
        experiment.uid = self.comps_experiment.id
        return experiment

    @staticmethod
    def _get_file_for_collection(collection_id: 'uuid', file_path: str):
        print(f"Cache miss for {collection_id} {file_path}")

        # retrieve the collection
        ac = AssetCollection.get(collection_id, QueryCriteria().select_children('assets'))

        # Look for the asset file in the collection
        file_name = ntpath.basename(file_path)
        path = ntpath.dirname(file_path).lstrip(f"Assets\\")

        for asset_file in ac.assets:
            if asset_file.file_name == file_name and (asset_file.relative_path or '') == path:
                return asset_file.retrieve()
        return None

    def get_files(self, item: 'TItem', files: 'List[str]') -> dict:
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

    def initialize_for_analysis(self, items: 'TItemList', analyzers: 'TAnalyzerList') -> NoReturn:
        # run any necessary analysis prep steps on groups of items (hierarchy level > 0)
        for analyzer in analyzers:
            analyzer.per_group(items=items)

    def get_object(self, id: 'uuid', level: int) -> Any:
        # Returned objects must have .level set to an integer (e.g. 0, 1, 2, ...)
        if level == 0:
            raise Exception(f'Unknown id hierarchy level {level} for platform: {self.__class__.__name__}')
        elif level == 1:
            object = self._retrieve_experiment(experiment_id=id)
        elif level == 2:
            raise Exception(f'Unknown id hierarchy level {level} for platform: {self.__class__.__name__}')
        else:
            raise Exception(f'Unknown id hierarchy level {level} for platform: {self.__class__.__name__}')
        return object

    def get_objects_by_relationship(self, object, relationship: int) -> list:
        target_level = object.level + relationship
        if target_level == 0:
            target_objects = self._retrieve_simulations(experiment=object)
        elif target_level == 1:
            raise Exception(f'Unknown how to retrieve relative objects for hierarchy level {object.level} '
                            f'for platform: {self.__class__.__name__}')
        elif target_level == 2:
            raise Exception(f'Unknown how to retrieve relative objects for hierarchy level {object.level} '
                            f'for platform: {self.__class__.__name__}')
        else:
            raise Exception(f'No relative objects for hierarchy level {object.level} '
                            f'for platform: {self.__class__.__name__}')
        return target_objects

    #
    # platform-specific convenience methods for dealing with domain-specific terminology.
    # possibly move out to a multi-inherited interface (for internal IDM platforms)
    #

    def get_simulation(self, sim_id: 'uuid') -> Any:
        return self.get_object(id=sim_id, level=0)

    def get_experiment(self, exp_id: 'uuid') -> 'TExperiment':
        return self.get_object(id=exp_id, level=1)

    def get_suite(self, suite_id: 'uuid') -> Any:
        return self.get_object(id=suite_id, level=2)

    def get_simulations_in_experiment(self, experiment: 'TExperiment') -> 'TSimulationList':
        return self.get_objects_by_relationship(object=experiment, relationship=self.CHILD)

    def get_experiments_in_suite(self, suite) -> 'List[TExperiment]':
        return self.get_objects_by_relationship(object=suite, relationship=self.CHILD)

    def get_experiment_for_simulation(self, simulation: 'TSimulation') -> 'TExperiment':
        return self.get_objects_by_relationship(object=simulation, relationship=self.PARENT)[0]

    def get_suite_for_experiment(self, experiment: 'TExperiment') -> Any:
        return self.get_objects_by_relationship(object=experiment, relationship=self.PARENT)
