import os

from COMPS import Client
from COMPS.Data import Configuration, Experiment, AssetCollection, AssetCollectionFile, Simulation, SimulationFile

from idmtools.entities import IPlatform, IExperiment
from idmtools.utils.time import timestamp


class COMPSPriority:
    Lowest = "Lowest"
    BelowNormal = "BelowNormal"
    Normal = "Normal"
    AboveNormal = "AboveNormal"
    Highest = "Highest"


class COMPSPlatform(IPlatform):
    """
    Represents the platform allowing to run simulations on COMPS.
    """
    MAX_SUBDIRECTORY_LENGTH = 35  # avoid maxpath issues on COMPS

    def __init__(self, endpoint: str = None, environment: str = None, priority: COMPSPriority = None):
        self.endpoint = endpoint or "https://comps2.idmod.org"
        self.environment = environment or "Bayesian"
        self.priority = priority or COMPSPriority.Lowest
        self.simulation_root = "$COMPS_PATH(USER)\output"
        self.node_group = "emod_abcd"
        self.num_retires = 0
        self.num_cores = 1
        self.exclusive = False
        self.comps_experiment = None
        self._login()

    def _login(self):
        try:
            Client.auth_manager()
        except:
            Client.login(self.endpoint)

    def send_assets_for_experiment(self, experiment):
        ac = AssetCollection()
        for asset in experiment.assets:
            ac.add_asset(AssetCollectionFile(file_name=asset.filename, relative_path=asset.relative_path),
                         data=asset.content)
        ac.save()
        experiment.assets.uid = ac.id
        print("Asset collection for experiment: {}".format(ac.id))

    def send_assets_for_simulation(self, simulation):
        pass

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

    def create_experiment(self, experiment: IExperiment):
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

        e = Experiment(name=experiment_name,
                       configuration=config,
                       suite_id=experiment.suite_id)

        # Add tags if present
        if experiment.tags: e.set_tags(experiment.tags)

        # Save the experiment
        e.save()
        self.comps_experiment = e

        experiment.uid = str(e.id)
        self.send_assets_for_experiment(experiment)

    def create_simulations(self, experiment: IExperiment):
        self._login()
        created_simulations = []
        for simulation in experiment.simulations:
            s = Simulation(name=experiment.name, experiment_id=experiment.uid,
                           configuration=Configuration(asset_collection_id=experiment.assets.uid))

            for asset in simulation.assets:
                s.add_file(simulationfile=SimulationFile(asset.filename, 'input'), data=asset.content)
            s.set_tags(simulation.tags)
            created_simulations.append(s)

        Simulation.save_all()

        # Register the IDs
        for i, comps_simulation in enumerate(created_simulations):
            experiment.simulations[i].uid = comps_simulation.id

    def run_simulations(self, experiment: IExperiment):
        self._login()
        self.comps_experiment.commission()
