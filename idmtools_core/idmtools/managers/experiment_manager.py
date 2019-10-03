import typing
from idmtools.core import EntityStatus
from idmtools.services.experiments import ExperimentPersistService
from idmtools.services.platforms import PlatformPersistService
from idmtools.utils.entities import retrieve_experiment

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
    def from_experiment_id(cls, experiment_id, platform):
        experiment = retrieve_experiment(experiment_id, platform)
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

    def simulation_batch_worker_thread(self, simulation_batch):
        for simulation in simulation_batch:
            simulation.pre_creation()

        ids = self.platform.create_simulations(simulation_batch)

        for uid, simulation in zip(ids, simulation_batch):
            simulation.uid = uid
            simulation.post_creation()

        return simulation_batch

    def create_simulations(self):
        """
        Create all the simulations contained in the experiment on the platform.
        """
        from concurrent.futures.thread import ThreadPoolExecutor
        from idmtools.core import EntityContainer

        with ThreadPoolExecutor(max_workers=16) as executor:
            results = executor.map(self.simulation_batch_worker_thread,
                                   self.experiment.batch_simulations(batch_size=10))

        _sims = EntityContainer()
        for sim_batch in results:
            for simulation in sim_batch:
                _sims.append(simulation.metadata)
                _sims.set_status(EntityStatus.CREATED)

        self.experiment.simulations = _sims

    def start_experiment(self):
        self.platform.run_simulations(self.experiment)
        self.experiment.simulations.set_status(EntityStatus.RUNNING)

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

        # Create the simulations on the platform
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
