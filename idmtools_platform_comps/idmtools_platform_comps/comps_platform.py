import json
import logging
import ntpath
import os
import uuid
from dataclasses import dataclass, field

from COMPS import Client
from COMPS.Data import AssetCollection, AssetCollectionFile, Configuration, Experiment as COMPSExperiment, \
    QueryCriteria, Simulation as COMPSSimulation, SimulationFile, Suite as COMPSSuite
from COMPS.Data.Simulation import SimulationState

from idmtools.core import CacheEnabled
from idmtools.core.enums import EntityStatus, ObjectType
from idmtools.core.experiment_factory import experiment_factory
from idmtools.entities import IPlatform
from idmtools.entities.iexperiment import TExperiment
from idmtools.entities.suite import Suite
from idmtools.utils.time import timestamp

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
        super().__post_init__()
        print("\nUser Login:")
        print(json.dumps({"endpoint": self.endpoint, "environment": self.environment}, indent=3))
        self._login()

    def _login(self):
        try:
            Client.auth_manager()
        except RuntimeError:
            Client.login(self.endpoint)

    def send_assets_for_experiment(self, experiment: TExperiment, **kwargs):
        if experiment.assets.count == 0:
            return

        ac = AssetCollection()
        for asset in experiment.assets:
            ac.add_asset(AssetCollectionFile(file_name=asset.filename, relative_path=asset.relative_path),
                         data=asset.content)
        ac.save()
        experiment.assets.uid = ac.id
        print("Asset collection for experiment: {}".format(ac.id))

    def send_assets_for_simulation(self, simulation, comps_simulation):
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

    def create_experiment(self, experiment: 'TExperiment'):
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

        experiment.uid = e.id
        self.send_assets_for_experiment(experiment)

    def create_simulations(self, simulation_batch):
        self._login()
        created_simulations = []

        for simulation in simulation_batch:
            s = COMPSSimulation(name=simulation.experiment.name, experiment_id=simulation.experiment.uid,
                                configuration=Configuration(asset_collection_id=simulation.experiment.assets.uid))

            self.send_assets_for_simulation(simulation, s)
            s.set_tags(simulation.tags)
            created_simulations.append(s)

        COMPSSimulation.save_all(None, save_semaphore=COMPSSimulation.get_save_semaphore())

        # Register the IDs
        return [s.id for s in created_simulations]

    def run_simulations(self, experiment: TExperiment):
        comps_experiment = self.get_object(experiment.uid, raw=True, object_type=ObjectType.EXPERIMENT)
        comps_experiment.commission()

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

    def refresh_experiment_status(self, experiment):
        # Do nothing if we are already done
        if experiment.done:
            return

        experiment.simulations.clear()
        self.restore_simulations(experiment)

    def restore_simulations(self, experiment: TExperiment) -> None:
        for s in self.get_children(experiment.uid, force=True, object_type=ObjectType.EXPERIMENT):
            experiment.simulations.append(s)

    def _get_experiment(self, experiment_id: 'uuid', query_criteria=None) -> 'COMPSExperiment':
        self._login()
        try:
            return COMPSExperiment.get(id=experiment_id,
                                       query_criteria=query_criteria or QueryCriteria().select(
                                           ["id", "name"]).select_children(["tags"]))
        except RuntimeError:
            return

    def _get_simulation(self, simulation_id: 'uuid', query_criteria=None) -> 'COMPSSimulation':
        self._login()
        try:
            return COMPSSimulation.get(id=simulation_id,
                                       query_criteria=query_criteria or QueryCriteria().select(
                                           ["id", "name", "experiment_id"]).select_children(["tags"]))
        except RuntimeError:
            return

    def _get_suite(self, suite_id: 'uuid', query_criteria=None) -> 'COMPSSuite':
        self._login()
        try:
            return COMPSSuite.get(id=suite_id, query_criteria=query_criteria or QueryCriteria().select(
                ["id", "name"]).select_children(["tags"]))
        except RuntimeError:
            return

    def _create_simulation(self, platform_simulation, experiment=None):
        # Recreate the experiment if needed
        experiment = experiment or self.get_object(platform_simulation.experiment_id)
        sim = experiment.simulation()
        sim.uid = platform_simulation.id
        sim.tags = platform_simulation.tags
        sim.platform_id = self.uid
        sim.status = COMPSPlatform._convert_COMPS_status(platform_simulation.state)
        return sim

    def _create_experiment(self, platform_experiment):
        experiment = experiment_factory.create(platform_experiment.tags.get("type"), tags=platform_experiment.tags,
                                               name=platform_experiment.name)
        experiment.uid = platform_experiment.id
        experiment.platform_id = self.uid
        experiment.comps_experiment = platform_experiment
        return experiment

    def _create_suite(self, platform_suite):
        suite = Suite(name=platform_suite.name)
        suite.uid = platform_suite.id
        experiments = self.get_children(suite.uid, object_type=ObjectType.SUITE)
        for ce in experiments:
            suite.experiments.append(self._create_experiment(ce))
        return suite

    def get_object(self, object_id, force=False, raw=False, object_type=None, query_criteria=None) -> any:
        cache_key = f"o_{object_id}_" + ('r' if raw else 'o')
        if force:
            self.cache.delete(cache_key)

        if cache_key not in self.cache:
            if object_type == ObjectType.EXPERIMENT:
                ce = self._get_experiment(object_id, query_criteria=query_criteria)
            elif object_type == ObjectType.SIMULATION:
                ce = self._get_simulation(object_id, query_criteria=query_criteria)
            elif object_type == ObjectType.SUITE:
                ce = self._get_suite(object_id, query_criteria=query_criteria)
            else:
                ce = self._get_experiment(object_id, query_criteria=query_criteria) \
                     or self._get_simulation(object_id, query_criteria=query_criteria) \
                     or self._get_suite(object_id, query_criteria=query_criteria)

            if not ce:
                raise Exception("Object not found on the platform")

            if raw:
                self.cache.set(cache_key, ce, expire=60)
            else:
                if isinstance(ce, COMPSExperiment):
                    self.cache.set(cache_key, self._create_experiment(ce), expire=60)
                elif isinstance(ce, COMPSSimulation):
                    self.cache.set(cache_key, self._create_simulation(ce), expire=60)
                elif isinstance(ce, COMPSSuite):
                    self.cache.set(cache_key, self._create_suite(ce), expire=60)

        return self.cache.get(cache_key)

    def get_parent(self, object_id, force=False, object_type=None, raw=False):
        cache_key = f'p_{object_id}' + ('r' if raw else 'o')
        if force:
            self.cache.delete(cache_key)

        if cache_key not in self.cache:
            ce = self.get_object(object_id, raw=True, object_type=object_type)

            if isinstance(ce, COMPSExperiment):
                obj = self.get_object(ce.suite_id, object_type=ObjectType.SUITE, raw=raw) if ce.suite_id else None
            elif isinstance(ce, COMPSSuite):
                obj = None
            elif isinstance(ce, COMPSSimulation):
                obj = self.get_object(ce.experiment_id, object_type=ObjectType.EXPERIMENT,
                                      raw=raw) if ce.experiment_id else None

            self.cache.set(cache_key, obj, expire=60)

        return self.cache.get(cache_key)

    def get_children(self, object_id, force=False, object_type=None, raw=False):
        cache_key = f"c_{object_id}" + ('r' if raw else 'o')
        if force:
            self.cache.delete(cache_key)

        if cache_key not in self.cache:
            ce = self.get_object(object_id, raw=True, object_type=object_type)

            if isinstance(ce, COMPSExperiment):
                children = ce.get_simulations(
                    query_criteria=QueryCriteria().select(["id", "state"]).select_children(["tags"]))
                if not raw:
                    experiment = self._create_experiment(ce)
                    children = [self._create_simulation(s, experiment) for s in children]
            elif isinstance(ce, COMPSSuite):
                children = [self.get_object(e.id, object_type=ObjectType.EXPERIMENT, raw=raw) for e in
                            COMPSExperiment.get(query_criteria=QueryCriteria().where("suite_id={}".format(ce.id)))]
            elif isinstance(ce, COMPSSimulation):
                children = None

            self.cache.set(cache_key, children, expire=60)

        return self.cache.get(cache_key)

    @staticmethod
    def _get_file_for_collection(collection_id, file_path):
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

    def get_assets_for_simulation(self, simulation, output_files):
        self._login()

        # Retrieve the simulation from COMPS
        comps_simulation = COMPSSimulation.get(simulation.uid,
                                               query_criteria=QueryCriteria().select(['id']).select_children(
                                                   ["files", "configuration"]))

        # Separate the output files in 2 groups:
        # - one for the transient files (retrieved through the comps simulation)
        # - one for the asset collection files (retrieved through the asset collection)
        all_paths = set(output_files)
        assets = set(path for path in all_paths if path.lower().startswith("assets"))
        transients = all_paths.difference(assets)

        # Create the return dict
        ret = {}

        # Retrieve the transient if any
        if transients:
            transients_files = comps_simulation.retrieve_output_files(paths=transients)
            ret = dict(zip(transients, transients_files))

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
