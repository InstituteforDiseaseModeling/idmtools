import typing
from prettytable import PrettyTable


from idmtools.services.experiments import ExperimentPersistService
from idmtools.services.platforms import PlatformPersistService

if typing.TYPE_CHECKING:
    from idmtools.core.types import TExperiment, TPlatform


class ExperimentManager:
    """
    Manages an experiment.
    """

    def __init__(self, experiment: 'TExperiment', platform: 'TPlatform'):
        """
        Constructor
        Args:
            experiment: The experiment to manage
        """
        self.platform = platform
        self.experiment = experiment
        self.printout = PrettyTable(["Simulation id", "Experiment id", "Input"])

    @classmethod
    def from_experiment_id(cls, experiment_id):
        experiment = ExperimentPersistService.retrieve(experiment_id)
        platform = PlatformPersistService.retrieve(experiment.platform_id)
        return cls(experiment, platform)

    def create_experiment(self):
        # Create experiment
        self.platform.create_experiment(self.experiment)
        # Persist the platform
        PlatformPersistService.save(self.platform)
        self.experiment.platform_id = self.platform.uid
        ExperimentPersistService.save(self.experiment)

    def create_simulations(self):
        """
        Create all the simulations contained in the experiment on the platform.
        """
        # Execute the builder if present
        if self.experiment.builder:
            self.experiment.execute_builder()
        elif not self.experiment.simulations:
            self.experiment.simulations = [self.experiment.simulation()]

        # Gather the assets
        for simulation in self.experiment.simulations:
            simulation.gather_assets()

        # Send the experiment to the platform
        self.platform.create_simulations(self.experiment)

        # Refresh experiment status
        self.refresh_status()

    def start_experiment(self):
        self.platform.run_simulations(self.experiment)
        self.refresh_status()

    def run(self):
        """
        Main entry point of the manager.
        - Create the experiment
        - Execute the builder (if any) to generate all the simulations
        - Create the simulations on the platform
        - Trigger the run on the platform
        """
        # Create experiment on the platform
        self.create_experiment()

        # Create the simulations the platform
        self.create_simulations()


        print(self.experiment)

        # Run
        self.start_experiment()

        for simulation in self.experiment.simulations:
            self.printout.add_row([simulation.uid, simulation.experiment_id, simulation.tags])


        print(self.printout)

    def wait_till_done(self, timeout: 'int' = 60 * 60 * 24, refresh_interval: 'int' = 5):
        """
        Wait for the experiment to be done
        Args:
            refresh_interval: How long in between polling
            timeout: How long to wait before failing
        """
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            self.refresh_status()
            if self.experiment.done:
                return
            time.sleep(refresh_interval)
        raise TimeoutError(f"Timeout of {timeout} seconds exceeded when monitoring experiment {self.experiment}")

    def refresh_status(self):
        self.platform.refresh_experiment_status(self.experiment)
        ExperimentPersistService.save(self.experiment)
