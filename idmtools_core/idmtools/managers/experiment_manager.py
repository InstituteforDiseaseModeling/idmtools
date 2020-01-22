import copy
from itertools import chain
from logging import getLogger, DEBUG
from typing import Set, Optional, Dict, Union
from more_itertools import grouper
from idmtools.core import EntityStatus, ExperimentBuilder, TExperimentBuilder
from idmtools.entities import IPlatform, Suite, ISimulation
from idmtools.entities.experiment import Experiment
from idmtools.entities.itask import ITask
from idmtools.entities.simulation import Simulation
from idmtools.services.experiments import ExperimentPersistService

logger = getLogger(__name__)


class ExperimentManager:
    """
    Class that manages an experiment.
    """

    def __init__(self, platform: IPlatform, base_task: Optional[ITask] = None,
                 base_simulation: Optional[ISimulation] = None, experiment_name: Optional[str] = None,
                 experiment_tags: Optional[Dict[str, str]] = None,
                 experiment: Optional[Experiment] = None, suite: Optional[Suite] = None,
                 builders: Union[Set[ExperimentBuilder], ExperimentBuilder] = None):
        """
        A constructor.

        Args:
            experiment: The experiment to manage
            platform: The platform to use
            suite: The suite to use
        """
        self.suite = suite
        if base_simulation is None and base_task is None:
            raise ValueError("Either an experiment, a base simulation, or a base task is required")

        if experiment is None:
            self.experiment = Experiment(name=experiment_name, tags=experiment_tags, platform=platform)
        else:
            self.experiment = experiment

        if base_simulation is None:
            self.base_simulation = Simulation(task=base_task, platform=platform)

        task_type = type(base_task)
        self.experiment.task_type = f'{task_type.__module__}.{task_type.__name__}'
        self.platform = platform
        self.experiment.platform = platform
        builders = self._validate_builders(builders)
        self.builders: Set[ExperimentBuilder] = builders if builders else set()

    @staticmethod
    def _validate_builders(builders):
        if builders and not isinstance(builders, set):
            if isinstance(builders, list):
                builders = set(builders)
            elif isinstance(builders, ExperimentBuilder):
                builders = []
            else:
                raise ValueError("Builders must be a list/set of builders or a single ExperimentBuilder")
        return builders

    def _new_simulation(self) -> Simulation:
        """
        Return a new simulation object.
        The simulation will be copied from the base simulation of the experiment.

        Returns:
            The created simulation.
        """
        # TODO: the experiment should be frozen when the first simulation is created
        sim = copy.deepcopy(self.base_simulation)
        sim.task = copy.deepcopy(self.base_simulation.task)
        sim.assets = copy.deepcopy(self.base_simulation.assets)
        sim.platform = self.platform
        sim.experiment = self.experiment
        return sim

    def _batch_simulations(self, batch_size=5):
        # If no builders and no simulation, just return the base simulation
        if not self.builders and not self.experiment.simulations:
            yield (self._new_simulation(),)
            return

        # First consider the simulations of the experiment
        if self.experiment.simulations:
            for sim in self.experiment.simulations:
                sim.platform = self.platform
                sim.experiment = self.experiment

            for groups in grouper(self.experiment.simulations, batch_size):
                sims = []
                for sim in filter(None, groups):
                    sims.append(sim)
                yield sims

        # Then the builders
        for groups in grouper(chain(*self.builders), batch_size):
            sims = []
            for simulation_functions in filter(None, groups):
                simulation = self._new_simulation()
                tags = {}

                for func in simulation_functions:
                    new_tags = func(simulation=simulation)
                    if new_tags:
                        tags.update(new_tags)

                simulation.tags.update(tags)
                sims.append(simulation)

            yield sims

    @property
    def builder(self) -> TExperimentBuilder:

        """
        For backward-compatibility purposes.

        Returns:
            The last ``TExperimentBuilder``.
        """
        return list(self.builders)[-1] if self.builders and len(self.builders) > 0 else None

    @builder.setter
    def builder(self, builder: TExperimentBuilder) -> None:
        """
        For backward-compatibility purposes.

        Args:
            builder: The new builder to be used.

        Returns:
            None
        """

        # Make sure we only take the last builder assignment
        if self.builders:
            self.builders.clear()

        self.add_builder(builder)

    def add_builder(self, builder: TExperimentBuilder) -> None:
        """
        Add builder to builder collection.

        Args:
            builder: A builder to be added.

        Returns:
            None
        """
        from idmtools.builders import ExperimentBuilder

        # Add builder validation
        if not isinstance(builder, ExperimentBuilder):
            raise Exception("Builder ({}) must have type of ExperimentBuilder!".format(builder))

        # Initialize builders the first time
        if self.builders is None:
            self.builders = set()

        # Add new builder to the collection
        self.builders.add(builder)

    def create_suite(self):
        # If no suite present -> do nothing
        if not self.suite or self.suite.status == EntityStatus.CREATED:
            return

        # Create the suite on the platform
        self.suite.pre_creation()
        self.platform.create_items([self.suite])
        self.suite.post_creation()

        # Add experiment to the suite
        self.suite.add_experiment(self.experiment)

    def create_experiment(self):
        # Do not recreate experiment
        if self.experiment.status == EntityStatus.CREATED:
            return

        self.experiment.pre_creation()

        # Create experiment
        self.platform.create_items(items=[self.experiment])  # noqa: F841

        # Make sure to link it to the experiment
        self.experiment.platform = self.platform

        self.experiment.post_creation()

        # Save the experiment
        ExperimentPersistService.save(self.experiment)

    def _simulation_batch_worker_thread(self, simulation_batch):
        logger.debug(f'Create {len(simulation_batch)} simulations')
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
        from idmtools.core import EntityContainer

        # Consider values from the block that Platform uses
        _max_workers = IdmConfigParser.get_option(None, "max_workers")
        _batch_size = IdmConfigParser.get_option(None, "batch_size")

        _max_workers = int(_max_workers) if _max_workers else 16
        _batch_size = int(_batch_size) if _batch_size else 10

        with ThreadPoolExecutor(max_workers=16) as executor:
            results = executor.map(self._simulation_batch_worker_thread,  # noqa: F841
                                   self._batch_simulations(batch_size=_batch_size))

        _sims = EntityContainer()
        for sim_batch in results:
            for simulation in sim_batch:
                _sims.append(simulation)

        self.experiment.simulations = _sims

    def start_experiment(self):
        self.platform.run_items([self.experiment])
        self.experiment.simulations.set_status(EntityStatus.RUNNING)

    def run(self):
        """
        Main entry point of the manager:

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

    def wait_till_done(self, timeout: int = 60 * 60 * 24, refresh_interval: int = 5):
        """
        Wait for the experiment to be done.

        Args:
            refresh_interval: How long to wait between polling.
            timeout: How long to wait before failing.
        """
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            if logger.isEnabledFor(DEBUG):
                logger.debug("Refreshing simulation status")
            self.refresh_status()
            if self.experiment.done:
                logger.debug("Experiment Done")
                return
            time.sleep(refresh_interval)
        raise TimeoutError(f"Timeout of {timeout} seconds exceeded when monitoring experiment {self.experiment}")

    def refresh_status(self):
        self.platform.refresh_status(item=self.experiment)
        ExperimentPersistService.save(self.experiment)
