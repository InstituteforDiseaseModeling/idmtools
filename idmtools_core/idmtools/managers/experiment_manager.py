import typing
from idmtools.core import EntityStatus
from idmtools.entities.iplatform import TPlatform
from idmtools.services.experiments import ExperimentPersistService
from idmtools.services.platforms import PlatformPersistService
from idmtools.utils.entities import retrieve_experiment

if typing.TYPE_CHECKING:
    from idmtools.entities.iexperiment import TExperiment
    from idmtools.entities.isuite import TSuite


class ExperimentManager:
    """
    Manages an experiment.
    """

    def __init__(self, experiment: 'TExperiment', platform: TPlatform, suite: 'TSuite' = None):
        """
        Constructor
        Args:
            experiment: The experiment to manage
            platform: The platform to use
            suite: The suite to use
        """
        self.suite = suite
        self.experiment = experiment
        self.platform = platform
        self.experiment.platform = platform

    @classmethod
    def from_experiment_id(cls, experiment_id, platform):
        experiment = retrieve_experiment(experiment_id, platform, with_simulations=True)
        platform = PlatformPersistService.retrieve(experiment.platform.uid)
        # cache miss, add the platform
        if platform is None:
            PlatformPersistService.save(obj=experiment.platform)
            platform = PlatformPersistService.retrieve(experiment.platform.uid)
        em = cls(experiment, platform)
        return em

    def create_suite(self):
        """
        Create a suite from platform and link it to experiment
        Returns: None
        """
        if self.suite is None:
            return

        # Create suite
        self.platform.create_items(items=[self.suite])

        # Make sure to link experiment to the suite
        self.experiment.suite_id = self.suite.uid
        self.experiment.suite = self.suite

        # Add experiment to the suite
        self.suite.experiments.append(self.experiment)

    def create_experiment(self):
        self.experiment.pre_creation()

        # Create experiment
        self.platform.create_items(items=[self.experiment])  # noqa: F841

        # Persist the platform
        PlatformPersistService.save(self.platform)

        # Make sure to link it to the experiment
        self.experiment.platform = self.platform

        self.experiment.post_creation()

        # Save the experiment
        ExperimentPersistService.save(self.experiment)

    def simulation_batch_worker_thread(self, simulation_batch):
        for simulation in simulation_batch:
            simulation.pre_creation()

        ids = self.platform.create_items(items=simulation_batch)

        for uid, simulation in zip(ids, simulation_batch):
            simulation.uid = uid
            simulation.post_creation()
        return simulation_batch

    def create_simulations(self):
        """
        Create all the simulations contained in the experiment on the platform.
        """
        from idmtools.config import IdmConfigParser
        from concurrent.futures.thread import ThreadPoolExecutor

        # Consider values from the block that Platform uses
        _max_workers = IdmConfigParser.get_option(None, "max_workers")
        _batch_size = IdmConfigParser.get_option(None, "batch_size")

        _max_workers = int(_max_workers) if _max_workers else 16
        _batch_size = int(_batch_size) if _batch_size else 10

        with ThreadPoolExecutor(max_workers=16) as executor:
            results = executor.map(self.simulation_batch_worker_thread,  # noqa: F841
                                   self.experiment.batch_simulations(batch_size=_batch_size))
        for sim_batch in results:
            for simulation in sim_batch:
                self.experiment.simulations.append(simulation.metadata)
                self.experiment.simulations.set_status(EntityStatus.CREATED)

    def start_experiment(self):
        self.platform.run_items([self.experiment])
        self.experiment.simulations.set_status(EntityStatus.RUNNING)

    def run(self):
        """
        Main entry point of the manager.
        - Create the suite
        - Create the experiment
        - Execute the builder (if any) to generate all the simulations
        - Create the simulations on the platform
        - Trigger the run on the platform
        """
        # Create suite on the platform
        self.create_suite()

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
        self.platform.refresh_status(item=self.experiment)
        ExperimentPersistService.save(self.experiment)
