from abc import ABC, abstractmethod
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from types import GeneratorType
from typing import Type, Any, NoReturn, Tuple, List, Dict, Iterator, Union
from uuid import UUID

from idmtools.core import EntityStatus
from idmtools.entities.experiment import Experiment


@dataclass
class IPlatformExperimentOperations(ABC):
    platform: 'IPlatform'
    platform_type: Type

    @abstractmethod
    def get(self, experiment_id: UUID, **kwargs) -> Any:
        """
        Returns the platform representation of an Experiment

        Args:
            experiment_id: Item id of Experiments
            **kwargs:

        Returns:
            Platform Representation of an experiment
        """
        pass

    def pre_create(self, experiment: Experiment, **kwargs) -> NoReturn:
        """
        Run the platform/experiment post creation events

        Args:
            experiment: Experiment to run post-creation events
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            NoReturn
        """
        experiment.pre_creation()

    def post_create(self, experiment: Experiment, **kwargs) -> NoReturn:
        """
        Run the platform/experiment post creation events

        Args:
            experiment: Experiment to run post-creation events
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            NoReturn
        """
        experiment.post_creation()

    def create(self, experiment: Experiment, do_pre: bool = True, do_post: bool = True, **kwargs) -> \
            Union[Experiment]:
        """
        Creates an experiment from an IDMTools simulation object. Also performs local/platform pre and post creation
        events

        Args:
            experiment: Experiment to create
            do_pre: Perform Pre creation events for item
            do_post: Perform Post creation events for item
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Created platform item and the UUID of said item
        """
        if experiment.status is not None:
            return experiment
        if do_pre:
            self.pre_create(experiment, **kwargs)
        experiment._platform_object = self.platform_create(experiment, **kwargs)
        experiment.platform = self.platform
        if do_post:
            self.post_create(experiment, **kwargs)
        return experiment

    @abstractmethod
    def platform_create(self, experiment: Experiment, **kwargs) -> Any:
        """
        Creates an experiment from an IDMTools experiment object

        Args:
            experiment: Experiment to create
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Created platform item and the UUID of said item
        """
        pass

    def batch_create(self, experiments: List[Experiment], **kwargs) -> List[Tuple[Experiment]]:
        """
        Provides a method to batch create experiments

        Args:
            experiments: List of experiments to create
            **kwargs:

        Returns:
            List of tuples containing the create object and id of item that was created
        """
        ret = []
        for exp in experiments:
            ret.append(self.create(exp, **kwargs))
        return ret

    @abstractmethod
    def get_children(self, experiment: Any, **kwargs) -> List[Any]:
        """
        Returns the children of an experiment object

        Args:
            experiment: Experiment object
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Children of experiment object
        """
        pass

    @abstractmethod
    def get_parent(self, experiment: Any, **kwargs) -> Any:
        """
        Returns the parent of item. If the platform doesn't support parents, you should throw a TopLevelItem error

        Args:
            experiment:
            **kwargs:

        Returns:

        Raise:
            TopLevelItem
        """
        pass

    def to_entity(self, experiment: Any, **kwargs) -> Experiment:
        """
        Converts the platform representation of experiment to idmtools representation

        Args:
            experiment:Platform experiment object

        Returns:
            IDMTools experiment object
        """
        return experiment

    def pre_run_item(self, experiment: Experiment):
        """
        Trigger right before commissioning experiment on platform. This ensures that the item is created. It also
            ensures that the children(simulations) have also been created

        Args:
            experiment: Experiment to commission

        Returns:

        """
        # ensure the item is created before running
        # TODO what status are valid here? Create only?
        if experiment.status is None:
            self.create(experiment)

        # check sims
        if isinstance(experiment.simulations, (GeneratorType, Iterator)):
            experiment.simulations = self.platform.create_items(experiment.simulations)
        elif len(experiment.simulations) == 0:
            raise ValueError("You cannot have an experiment with now simulations")
        else:
            experiment.simulations = self.platform.create_items(experiment.simulations)

    def post_run_item(self, experiment: Experiment):
        """
        Trigger right after commissioning experiment on platform.

        Args:
            experiment: Experiment just commissioned

        Returns:

        """
        experiment.simulations.set_status(EntityStatus.RUNNING)

    def run_item(self, experiment: Experiment):
        """
        Called during commissioning of an item. This should create the remote resource

        Args:
            experiment:

        Returns:

        """
        self.pre_run_item(experiment)
        self.platform_run_item(experiment)
        self.post_run_item(experiment)

    @abstractmethod
    def platform_run_item(self, experiment: Experiment):
        """
        Called during commissioning of an item. This should perform what is needed to commission job on platform

        Args:
            experiment:

        Returns:

        """
        pass

    @abstractmethod
    def send_assets(self, experiment: Any):
        """
        Transfer Experiment assets to the platform.
        Args:
            experiment: Experiment to send assets for

        Returns:

        """
        pass

    @abstractmethod
    def refresh_status(self, experiment: Experiment):
        """
        Refresh status for experiment object. This should update the object directly. For experiments it is best if
        all simulation states are updated as well

        Args:
            experiment: Experiment to get status for

        Returns:
            None
        """
        pass

    def get_assets(self, experiment: Experiment, files: List[str], **kwargs) -> Dict[str, Dict[str, bytearray]]:
        """
        Get files from experiment

        Args:
            experiment: Experiment to get files from
            files: List files
            **kwargs:

        Returns:
            Dict with each sim id and the files contents matching specified list
        """
        ret = dict()
        for sim in experiment.simulations:
            ret[sim.uid] = self.platform._simulation.get_assets(sim, files, **kwargs)
        return ret

    def list_assets(self, experiment: Experiment) -> Dict[str, List[str]]:
        """
        List assets available for experiment

        Args:
            experiment: Experiment to get assets for

        Returns:
            Dictionary of simulation and assets on each sim
        """
        ret = {}
        with ThreadPoolExecutor() as pool:
            futures = dict()
            for sim in experiment.simulations:
                future = pool.submit(self.platform._simulations.list_assets, sim)
                futures[future] = sim

            for future in as_completed(futures):
                ret[futures[future]] = future.result()
        return ret