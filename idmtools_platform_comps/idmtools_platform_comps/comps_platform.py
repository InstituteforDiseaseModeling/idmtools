import logging
import ntpath
import os
import json

from COMPS import Client
from COMPS.Data import AssetCollection, AssetCollectionFile, Configuration, Experiment as COMPSExperiment, \
    QueryCriteria, Simulation as COMPSSimulation, SimulationFile
from COMPS.Data.Simulation import SimulationState
from dataclasses import dataclass, field

from idmtools.core import CacheEnabled
from idmtools.core.experiment_factory import experiment_factory
from idmtools.core.enums import EntityStatus
from idmtools.entities import IPlatform
from idmtools.entities.iexperiment import TExperiment
from idmtools.utils.time import timestamp
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
        self.comps_experiment = e

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

    def refresh_experiment_status(self, experiment):
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

    def restore_simulations(self, experiment: TExperiment) -> None:
        self._comps_experiment_id = experiment.uid

        for s in self.comps_experiment.get_simulations(
                query_criteria=QueryCriteria().select(["id", "state"]).select_children(["tags"])):
            sim = experiment.simulation()
            sim.uid = s.id
            sim.tags = s.tags
            sim.status = COMPSPlatform._convert_COMPS_status(s.state)
            experiment.simulations.append(sim)

    def retrieve_experiment(self, experiment_id: uuid) -> TExperiment:
        self._comps_experiment_id = experiment_id
        experiment = experiment_factory.create(self.comps_experiment.tags.get("type"), tags=self.comps_experiment.tags)
        experiment.uid = self.comps_experiment.id
        return experiment

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
