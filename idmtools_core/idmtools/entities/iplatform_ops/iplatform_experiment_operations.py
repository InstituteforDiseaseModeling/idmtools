"""
IPlatformExperimentOperations defines experiment item operations interface.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from abc import ABC, abstractmethod
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from logging import getLogger, DEBUG
from types import GeneratorType
from typing import Type, Any, NoReturn, Tuple, List, Dict, Iterator, Union, TYPE_CHECKING

from idmtools.assets import Asset
from idmtools.core.enums import EntityStatus, ItemType
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform_ops.utils import batch_create_items
from idmtools.registry.functions import FunctionPluginManager

logger = getLogger(__name__)
if TYPE_CHECKING:  # pragma: no cover
    from idmtools.entities.iplatform import IPlatform


@dataclass
class IPlatformExperimentOperations(ABC):
    """
    IPlatformExperimentOperations defines experiments item operations interface.
    """
    platform: 'IPlatform'  # noqa: F821
    platform_type: Type

    @abstractmethod
    def get(self, experiment_id: str, **kwargs) -> Any:
        """
        Returns the platform representation of an Experiment.

        Args:
            experiment_id: Item id of Experiments
            **kwargs:

        Returns:
            Platform Representation of an experiment
        """
        pass

    def pre_create(self, experiment: Experiment, **kwargs) -> NoReturn:
        """
        Run the platform/experiment post creation events.

        Args:
            experiment: Experiment to run post-creation events
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            NoReturn
        """
        if logger.isEnabledFor(DEBUG):
            logger.debug("Calling idmtools_platform_pre_create_item hooks")
        FunctionPluginManager.instance().hook.idmtools_platform_pre_create_item(item=experiment, kwargs=kwargs)
        if logger.isEnabledFor(DEBUG):
            logger.debug("Calling experiment pre_creation")
        experiment.pre_creation(self.platform)

    def post_create(self, experiment: Experiment, **kwargs) -> NoReturn:
        """
        Run the platform/experiment post creation events.

        Args:
            experiment: Experiment to run post-creation events
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            NoReturn
        """
        if logger.isEnabledFor(DEBUG):
            logger.debug("Calling idmtools_platform_post_create_item hooks")
        FunctionPluginManager.instance().hook.idmtools_platform_post_create_item(item=experiment, kwargs=kwargs)
        if logger.isEnabledFor(DEBUG):
            logger.debug("Calling experiment post_creation")
        experiment.post_creation(self.platform)

    def create(self, experiment: Experiment, do_pre: bool = True, do_post: bool = True, **kwargs) -> Union[Experiment]:
        """
        Creates an experiment from an IDMTools simulation object.

        Also performs local/platform pre and post creation events.

        Args:
            experiment: Experiment to create
            do_pre: Perform Pre creation events for item
            do_post: Perform Post creation events for item
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Created platform item and the id of said item
        """
        if experiment.status is not None:
            if logger.isEnabledFor(DEBUG):
                logger.debug("Calling experiment platform_modify_experiment")
            experiment = self.platform_modify_experiment(experiment, **kwargs)
            if logger.isEnabledFor(DEBUG):
                logger.debug("Finished platform_modify_experiment")
            return experiment
        if do_pre:
            self.pre_create(experiment, **kwargs)
            if logger.isEnabledFor(DEBUG):
                logger.debug("Finished pre_create")
        if logger.isEnabledFor(DEBUG):
            logger.debug("Calling platform_create")
        experiment._platform_object = self.platform_create(experiment, **kwargs)
        if logger.isEnabledFor(DEBUG):
            logger.debug("Finished platform_create")
        experiment.platform = self.platform
        if do_post:
            self.post_create(experiment, **kwargs)
            if logger.isEnabledFor(DEBUG):
                logger.debug("Finished post_create")
        return experiment

    @abstractmethod
    def platform_create(self, experiment: Experiment, **kwargs) -> Any:
        """
        Creates an experiment from an IDMTools experiment object.

        Args:
            experiment: Experiment to create
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Created platform item and the id of said item
        """
        pass

    def batch_create(self, experiments: List[Experiment], display_progress: bool = True, **kwargs) -> List[Tuple[Experiment]]:
        """
        Provides a method to batch create experiments.

        Args:
            experiments: List of experiments to create
            display_progress: Show progress bar
            **kwargs: Keyword arguments to pass to the batch

        Returns:
            List of tuples containing the create object and id of item that was created
        """
        return batch_create_items(experiments, create_func=self.create, display_progress=display_progress,
                                  progress_description="Creating Experiments", unit="experiment",
                                  **kwargs)

    @abstractmethod
    def get_children(self, experiment: Any, **kwargs) -> List[Any]:
        """
        Returns the children of an experiment object.

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
        Returns the parent of item. If the platform doesn't support parents, you should throw a TopLevelItem error.

        Args:
            experiment: Experiment to get parent from
            **kwargs:

        Returns:
            Parent of Experiment(Suite)

        Raise:
            TopLevelItem
        """
        pass

    def to_entity(self, experiment: Any, **kwargs) -> Experiment:
        """
        Converts the platform representation of experiment to idmtools representation.

        Args:
            experiment:Platform experiment object

        Returns:
            IDMTools experiment object
        """
        return experiment

    def pre_run_item(self, experiment: Experiment, **kwargs):
        """
        Trigger right before commissioning experiment on platform.

        This ensures that the item is created. It also ensures that the children(simulations) have also been created.

        Args:
            experiment: Experiment to commission

        Returns:
            None

        Raises:
            ValueError - If there are no simulations
        """
        if logger.isEnabledFor(DEBUG):
            logger.debug("Calling pre_run")
        experiment.pre_run(self.platform)
        # ensure the item is created before running
        if experiment.status is None:
            if logger.isEnabledFor(DEBUG):
                logger.debug("Calling create")
            self.create(experiment, **kwargs)
        else:
            if logger.isEnabledFor(DEBUG):
                logger.debug("Calling platform_modify_experiment")
            experiment = self.platform_modify_experiment(experiment, **kwargs)

        # check sims
        if logger.isEnabledFor(DEBUG):
            logger.debug("Ensuring simulations exist")
        if isinstance(experiment.simulations, (GeneratorType, Iterator)):
            if logger.isEnabledFor(DEBUG):
                logger.debug("Calling _create_items_of_type for sims")
            experiment.simulations = self.platform._create_items_of_type(experiment.simulations, ItemType.SIMULATION,
                                                                         **kwargs)
        elif len(experiment.simulations) == 0:
            raise ValueError("You cannot have an experiment with no simulations")
        else:
            if logger.isEnabledFor(DEBUG):
                logger.debug("Calling _create_items_of_type for sims")
            experiment.simulations = self.platform._create_items_of_type(experiment.simulations, ItemType.SIMULATION,
                                                                         **kwargs)
        if logger.isEnabledFor(DEBUG):
            logger.debug("Finished checking simulations")

    def post_run_item(self, experiment: Experiment, **kwargs):
        """
        Trigger right after commissioning experiment on platform.

        Args:
            experiment: Experiment just commissioned

        Returns:
            None
        """
        if logger.isEnabledFor(DEBUG):
            logger.debug("Calling idmtools_platform_post_run hooks")
        FunctionPluginManager.instance().hook.idmtools_platform_post_run(item=experiment, kwargs=kwargs)
        experiment.post_run(self.platform)

    def run_item(self, experiment: Experiment, **kwargs):
        """
        Called during commissioning of an item. This should create the remote resource.

        Args:
            experiment:Experiment
            **kwargs: Keyword arguments to pass to pre_run_item, platform_run_item, post_run_item

        Returns:
            None
        """
        if logger.isEnabledFor(DEBUG):
            logger.debug("Calling pre_run_item")
        self.pre_run_item(experiment, **kwargs)
        if experiment.status not in [EntityStatus.FAILED, EntityStatus.SUCCEEDED]:
            if logger.isEnabledFor(DEBUG):
                logger.debug("Calling platform_run_item")
            self.platform_run_item(experiment, **kwargs)
            if logger.isEnabledFor(DEBUG):
                logger.debug("Calling post_run_item")
            self.post_run_item(experiment, **kwargs)

    @abstractmethod
    def platform_run_item(self, experiment: Experiment, **kwargs):
        """
        Called during commissioning of an item. This should perform what is needed to commission job on platform.

        Args:
            experiment:

        Returns:
            None
        """
        pass

    @abstractmethod
    def send_assets(self, experiment: Any, **kwargs):
        """
        Transfer Experiment assets to the platform.

        Args:
            experiment: Experiment to send assets for

        Returns:
            None
        """
        pass

    @abstractmethod
    def refresh_status(self, experiment: Experiment, **kwargs):
        """
        Refresh status for experiment object.

        This should update the object directly. For experiments it is best if all simulation states are updated as well.

        Args:
            experiment: Experiment to get status for

        Returns:
            None
        """
        pass

    def get_assets(self, experiment: Experiment, files: List[str], **kwargs) -> Dict[str, Dict[str, bytearray]]:
        """
        Get files from experiment.

        Args:
            experiment: Experiment to get files from
            files: List files
            **kwargs:

        Returns:
            Dict with each sim id and the files contents matching specified list
        """
        ret = dict()
        for sim in experiment.simulations:
            ret[sim.uid] = self.platform._simulations.get_assets(sim, files, **kwargs)
        return ret

    def list_assets(self, experiment: Experiment, children: bool = False, **kwargs) -> List[Asset]:
        """
        List available assets for a experiment.

        Args:
            experiment: Experiment to list files for
            children: Should we load assets from children as well?

        Returns:
            List of Assets
        """
        ret = self.platform_list_asset(experiment, **kwargs)
        if children:
            with ThreadPoolExecutor() as pool:
                futures = dict()
                for sim in experiment.simulations:
                    future = pool.submit(self.platform._simulations.list_assets, sim, **kwargs)
                    futures[future] = sim

                for future in as_completed(futures):
                    result = future.result()
                    ret.extend(result)
        return ret

    def platform_list_asset(self, experiment: Experiment, **kwargs) -> List[Asset]:
        """
        List the assets on an experiment.

        Args:
            experiment: Experiment to list.
            **kwargs: Extra Arguments

        Returns:
            List of Assets
        """
        return []

    def platform_modify_experiment(self, experiment: Experiment, regather_common_assets: bool = False,
                                   **kwargs) -> Experiment:
        """
        API to allow detection of experiments already created.

        Args:
            experiment:
            regather_common_assets: When modifying, should we gather assets from template/simulations. It is important to note that when using this feature, ensure the previous simulations have finished provisioning. Failure to do so can lead to unexpected behaviour

        Returns:
            Experiment updated
        """
        return experiment

    def create_sim_directory_map(self, experiment_id: str) -> Dict:
        """
        Build simulation working directory mapping.
        Args:
            experiment_id: experiment id

        Returns:
            Dict
        """
        return {}

    def platform_delete(self, experiment_id: str) -> None:
        """
        Delete platform experiment.
        Args:
            experiment_id: experiment id
        Returns:
            None
        """
        pass

    def platform_cancel(self, experiment_id: str) -> None:
        """
        Cancel platform experiment.
        Args:
            experiment_id: experiment id
        Returns:
            None
        """
        pass
