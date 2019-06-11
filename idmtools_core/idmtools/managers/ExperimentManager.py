import typing

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

    @classmethod
    def from_experiment_id(cls, experiment_id):
        experiment = ExperimentPersistService.retrieve(str(experiment_id))
        platform = PlatformPersistService.retrieve(experiment.platform_id)
        em = cls(experiment, platform)
        em.restore_simulations()
        return em

    def restore_simulations(self):
        self.platform.restore_simulations(self.experiment)

    def create_experiment(self):
        self.experiment.pre_creation()

        # Create experiment
        self.platform.create_experiment(self.experiment)

        # Persist the platform
        PlatformPersistService.save(self.platform)
        self.experiment.platform_id = self.platform.uid

        self.experiment.post_creation()

        # Save the experiment
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

        # Call the pre_creation event on the simulations
        for simulation in self.experiment.simulations:
            simulation.pre_creation()

        # Send the experiment to the platform
        self.platform.create_simulations(self.experiment)

        for simulation in self.experiment.simulations:
            simulation.post_creation()

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

        # Display the experiment contents
        self.experiment.display()

        # Run
        self.start_experiment()

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
