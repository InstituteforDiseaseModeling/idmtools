import json
import logging
import ntpath
import os
import typing
from dataclasses import dataclass, field
from uuid import UUID

from COMPS import Client
from COMPS.Data import AssetCollection as COMPSAssetCollection, AssetCollectionFile, Configuration, \
    Experiment as COMPSExperiment, \
    QueryCriteria, Simulation as COMPSSimulation, SimulationFile, Suite as COMPSSuite

from idmtools.core import CacheEnabled, EntityContainer, ItemType
from idmtools.core.experiment_factory import experiment_factory
from idmtools.core.interfaces.ientity import IEntity, TEntityList
from idmtools.entities import IPlatform
from idmtools.entities.iexperiment import IExperiment, StandardExperiment
from idmtools.entities.isimulation import ISimulation
from idmtools.entities.suite import Suite
from idmtools.utils.time import timestamp
from idmtools_platform_comps.utils import convert_COMPS_status

if typing.TYPE_CHECKING:
    from typing import NoReturn, List, Dict
    from idmtools.entities.isuite import TSuite
    from idmtools.entities.iexperiment import TExperiment
    from idmtools.core.interfaces.iitem import TItemList

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

    def __post_init__(self):
        print("\nUser Login:")
        print(json.dumps({"endpoint": self.endpoint, "environment": self.environment}, indent=3))
        self._login()
        self.supported_types = {ItemType.EXPERIMENT, ItemType.SIMULATION, ItemType.SUITE, ItemType.ASSETCOLLECTION}
        super().__post_init__()

    def _login(self):
        try:
            Client.auth_manager()
        except RuntimeError:
            Client.login(self.endpoint)

    def send_assets(self, item, **kwargs) -> 'NoReturn':
        # TODO: add asset sending for suites if needed
        if isinstance(item, ISimulation):
            self._send_assets_for_simulation(simulation=item, **kwargs)
        elif isinstance(item, IExperiment):
            self._send_assets_for_experiment(experiment=item, **kwargs)
        else:
            raise Exception(f'Unknown how to send assets for item type: {type(item)} '
                            f'for platform: {self.__class__.__name__}')

    @staticmethod
    def _send_assets_for_experiment(experiment: 'TExperiment', **kwargs) -> 'NoReturn':

        if experiment.assets.count == 0:
            return

        ac = COMPSAssetCollection()
        for asset in experiment.assets:
            ac.add_asset(AssetCollectionFile(file_name=asset.filename, relative_path=asset.relative_path),
                         data=asset.content)
        ac.save()
        experiment.assets.uid = ac.id
        print("Asset collection for experiment: {}".format(ac.id))

        # associate the assets with the experiment in COMPS
        e = COMPSExperiment.get(id=experiment.uid)
        e.configuration = Configuration(asset_collection_id=ac.id)
        e.save()

    @staticmethod
    def _send_assets_for_simulation(simulation, comps_simulation) -> 'NoReturn':
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

    def _create_suite(self, suite: 'TSuite') -> 'UUID':
        """
        Create a COMPS Suite
        Args:
            suite: local suite to be used to create COMPS Suite
        Returns: None
        """
        self._login()

        # Create suite
        comps_suite = COMPSSuite(name=suite.name, description=suite.description)
        comps_suite.set_tags(suite.tags)
        comps_suite.save()

        # Update suite uid
        suite.uid = comps_suite.id
        return suite.uid

    def _create_experiment(self, experiment: 'TExperiment') -> 'UUID':
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

        # Set the ID back in the object
        experiment.uid = e.id

        # Send the assets for the experiment
        self.send_assets(item=experiment)

        return experiment.uid

    def _create_batch(self, batch: 'TEntityList', item_type: 'ItemType') -> 'List[UUID]':
        if item_type == ItemType.SIMULATION:
            created_simulations = []
            for simulation in batch:
                s = COMPSSimulation(name=simulation.experiment.name, experiment_id=simulation.experiment.uid,
                                    configuration=Configuration(asset_collection_id=simulation.experiment.assets.uid))
                self.send_assets(item=simulation, comps_simulation=s)
                s.set_tags(simulation.tags)
                created_simulations.append(s)
            COMPSSimulation.save_all(None, save_semaphore=COMPSSimulation.get_save_semaphore())
            return [s.id for s in created_simulations]
        elif item_type == ItemType.EXPERIMENT:
            ids = [self._create_experiment(experiment=item) for item in batch]
            return ids
        elif item_type == ItemType.SUITE:
            ids = [self._create_suite(suite=item) for item in batch]
            return ids
        else:
            raise Exception(f'Unable to create items of type: {item_type} for platform: {self.__class__.__name__}')

    def run_items(self, items: 'TItemList') -> 'NoReturn':
        for item in items:
            item.get_platform_object().commission()

    def get_platform_item(self, item_id, item_type, **kwargs):
        # Retrieve the eventual columns/children arguments
        cols = kwargs.get('columns')
        children = kwargs.get('children')

        self._login()

        if item_type == ItemType.SUITE:
            cols = cols or ["id", "name"]
            children = children if children is not None else ["tags", "configuration"]
            return COMPSSuite.get(id=item_id,
                                  query_criteria=QueryCriteria().select(cols).select_children(children))

        if item_type == ItemType.EXPERIMENT:
            cols = cols or ["id", "name", "suite_id"]
            children = children if children is not None else ["tags", "configuration"]
            return COMPSExperiment.get(id=item_id,
                                       query_criteria=QueryCriteria().select(cols).select_children(children))

        if item_type == ItemType.SIMULATION:
            cols = cols or ["id", "name", "experiment_id", "state"]
            children = children if children is not None else ["tags"]
            return COMPSSimulation.get(id=item_id,
                                       query_criteria=QueryCriteria().select(cols).select_children(children))

        if item_type == ItemType.ASSETCOLLECTION:
            children = children if children is not None else ["assets"]
            return COMPSAssetCollection.get(id=item_id, query_criteria=QueryCriteria().select_children(children))

    def _platform_item_to_entity(self, platform_item, **kwargs):
        if isinstance(platform_item, COMPSExperiment):
            # Recreate the suite if needed
            suite = kwargs.get('suite') or self.get_item(platform_item.suite_id,
                                                                   item_type=ItemType.SUITE)

            # Create an experiment
            obj = experiment_factory.create(platform_item.tags.get("type"), tags=platform_item.tags,
                                                   name=platform_item.name, fallback=StandardExperiment)

            # Set parent
            obj.parent = suite

            # Set the correct attributes
            obj.uid = platform_item.id
            obj.comps_experiment = platform_item
        elif isinstance(platform_item, COMPSSimulation):
            # Recreate the experiment if needed
            experiment = kwargs.get('experiment') or self.get_item(platform_item.experiment_id,
                                                                   item_type=ItemType.EXPERIMENT)
            # Get a simulation
            obj = experiment.simulation()
            # Set its correct attributes
            obj.uid = platform_item.id
            obj.tags = platform_item.tags
            obj.status = convert_COMPS_status(platform_item.state)
        elif isinstance(platform_item, COMPSSuite):
            # Creat a suite
            obj = Suite()

            # Set its correct attributes
            obj.uid = platform_item.id
            obj.name = platform_item.name
            obj.description = platform_item.description
            obj.tags = platform_item.tags
            obj.comps_suite = platform_item

        # Associate the platform
        obj.platform = self
        return obj

    def get_parent_for_platform_item(self, platform_item, raw=False, **kwargs):
        if isinstance(platform_item, COMPSExperiment):
            # For experiment -> find the suite
            return self.get_item(platform_item.suite_id, item_type=ItemType.SUITE, raw=raw,
                                 **kwargs) if platform_item.suite_id else None
        if isinstance(platform_item, COMPSSimulation):
            # For a simulation, find the experiment
            return self.get_item(platform_item.experiment_id, item_type=ItemType.EXPERIMENT,
                                 raw=raw, **kwargs) if platform_item.experiment_id else None
        # If Suite return None
        return None

    def get_children_for_platform_item(self, platform_item, raw=False, **kwargs):
        if isinstance(platform_item, COMPSExperiment):
            cols = kwargs.get("cols")
            children = kwargs.get("children")
            cols = cols or ["id", "name", "experiment_id", "state"]
            children = children if children is not None else ["tags"]

            children = platform_item.get_simulations(
                query_criteria=QueryCriteria().select(cols).select_children(children))
            if not raw:
                experiment = self._platform_item_to_entity(platform_item)
                return EntityContainer([self._platform_item_to_entity(s, experiment=experiment) for s in children])
            else:
                return children
        elif isinstance(platform_item, COMPSSuite):
            cols = kwargs.get("cols")
            children = kwargs.get("children")
            cols = cols or ["id", "name", "suite_id"]
            children = children if children is not None else ["tags"]

            children = platform_item.get_experiments(
                query_criteria=QueryCriteria().select(cols).select_children(children))
            if not raw:
                suite = self._platform_item_to_entity(platform_item)
                return EntityContainer([self._platform_item_to_entity(e, suite=suite) for e in children])
            else:
                return children

        return None

    def refresh_status(self, item) -> 'NoReturn':
        if isinstance(item, IExperiment):
            simulations = self.get_children(item.uid, ItemType.EXPERIMENT, force=True, raw=True, cols=["id", "state"],
                                            children=[])
            for s in simulations:
                item.simulations.set_status_for_item(s.id, convert_COMPS_status(s.state))

            return

        raise NotImplemented("comps_platform.refresh_status only implemented for Experiments")

    def _get_file_for_collection(self, collection_id: 'UUID', file_path: str) -> 'NoReturn':
        print(f"Cache miss for {collection_id} {file_path}")

        # retrieve the collection
        ac = self.get_item(collection_id, ItemType.ASSETCOLLECTION, raw=True)

        # Look for the asset file in the collection
        file_name = ntpath.basename(file_path)
        path = ntpath.dirname(file_path).lstrip(f"Assets\\")

        for asset_file in ac.assets:
            if asset_file.file_name == file_name and (asset_file.relative_path or '') == path:
                return asset_file.retrieve()

    def get_files(self, item: 'IEntity', files: 'List[str]') -> 'Dict':
        self._login()

        # Retrieve the simulation from COMPS
        comps_simulation = self.get_platform_item(item.uid, ItemType.SIMULATION,
                                                  columns=["id", "experiment_id"], children=["files", "configuration"])

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
