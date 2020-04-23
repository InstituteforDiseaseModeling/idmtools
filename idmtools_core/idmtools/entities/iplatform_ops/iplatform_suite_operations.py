from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Type, Any, List, Tuple, Dict, NoReturn
from uuid import UUID

from idmtools.core.enums import EntityStatus, ItemType
from idmtools.entities.iplatform_ops.utils import batch_create_items
from idmtools.entities.suite import Suite


@dataclass
class IPlatformSuiteOperations(ABC):
    platform: 'IPlatform'  # noqa: F821
    platform_type: Type

    @abstractmethod
    def get(self, suite_id: UUID, **kwargs) -> Any:
        """
        Returns the platform representation of an Suite

        Args:
            suite_id: Item id of Suites
            **kwargs:

        Returns:
            Platform Representation of an suite
        """
        pass

    def batch_create(self, suites: List[Suite], display_progress: bool = True, **kwargs) -> List[Tuple[Any, UUID]]:
        """
        Provides a method to batch create suites

        Args:
            display_progress: Display progress bar
            suites: List of suites to create
            **kwargs:

        Returns:
            List of tuples containing the create object and id of item that was created
        """
        return batch_create_items(suites, create_func=self.create, display_progress=display_progress,
                                  progress_description="Creating Suites",
                                  **kwargs)

    def pre_create(self, suite: Suite, **kwargs) -> NoReturn:
        """
        Run the platform/suite post creation events

        Args:
            suite: Experiment to run post-creation events
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            NoReturn
        """
        suite.pre_creation()

    def post_create(self, suite: Suite, **kwargs) -> NoReturn:
        """
        Run the platform/suite post creation events

        Args:
            suite: Experiment to run post-creation events
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            NoReturn
        """
        suite.status = EntityStatus.CREATED
        suite.platform = self.platform
        suite.post_creation()
        for experiment in suite.experiments:
            experiment.parent_id = suite.id

    def create(self, suite: Suite, do_pre: bool = True, do_post: bool = True, **kwargs) -> Tuple[Any, UUID]:
        """
        Creates an simulation from an IDMTools suite object. Also performs pre-creation and post-creation
        locally and on platform

        Args:
            suite: Suite to create
            do_pre: Perform Pre creation events for item
            do_post: Perform Post creation events for item
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Created platform item and the UUID of said item
        """
        if suite.status == EntityStatus.CREATED:
            return suite._platform_object, suite.uid
        if do_pre:
            self.pre_create(suite, **kwargs)
        ret = self.platform_create(suite, **kwargs)
        if do_post:
            self.post_create(suite, **kwargs)
        return ret

    @abstractmethod
    def platform_create(self, suite: Suite, **kwargs) -> Tuple[Any, UUID]:
        """
        Creates an suite from an IDMTools suite object

        Args:
            suite: Suite to create
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Created platform item and the UUID of said item
        """
        pass

    def pre_run_item(self, suite: Suite, **kwargs):
        """
        Trigger right before commissioning experiment on platform. This ensures that the item is created. It also
            ensures that the children(simulations) have also been created

        Args:
            suite: Experiment to commission

        Returns:

        """
        # ensure the item is created before running
        # TODO what status are valid here? Create only?
        if suite.status is None:
            self.create(suite)

        exps_to_commission = []
        for exp in suite.experiments:
            if exp.status is None:
                exps_to_commission.append(exp)
        if exps_to_commission:
            self.platform.create_items(exps_to_commission, **kwargs)
            self.platform.run_items(exps_to_commission, **kwargs)

    def post_run_item(self, suite: Suite, **kwargs):
        """
        Trigger right after commissioning suite on platform.

        Args:
            suite: Experiment just commissioned

        Returns:

        """
        suite.status = EntityStatus.RUNNING

    def run_item(self, suite: Suite, **kwargs):
        """
        Called during commissioning of an item. This should create the remote resource

        Args:
            workflow_item:

        Returns:

        """
        self.pre_run_item(suite)
        self.platform_run_item(suite)
        self.post_run_item(suite)

    def platform_run_item(self, suite: Suite, **kwargs):
        """
        Called during commissioning of an item. This should perform what is needed to commission job on platform

        Args:
            suite:

        Returns:

        """
        pass

    @abstractmethod
    def get_parent(self, suite: Any, **kwargs) -> Any:
        """
        Returns the parent of item. If the platform doesn't support parents, you should throw a TopLevelItem error

        Args:
            suite:
            **kwargs:

        Returns:

        Raise:
            TopLevelItem
        """
        pass

    @abstractmethod
    def get_children(self, suite: Any, **kwargs) -> List[Any]:
        """
        Returns the children of an suite object

        Args:
            suite: Suite object
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Children of suite object
        """
        pass

    def to_entity(self, suite: Any, **kwargs) -> Suite:
        """
        Converts the platform representation of suite to idmtools representation

        Args:
            suite:Platform suite object

        Returns:
            IDMTools suite object
        """
        return suite

    @abstractmethod
    def refresh_status(self, experiment: Suite, **kwargs):
        """
        Refresh status of suite
        Args:
            experiment:

        Returns:

        """
        pass

    def get_assets(self, suite: Suite, files: List[str], **kwargs) -> Dict[str, Dict[str, Dict[str, bytearray]]]:
        """
        Fetch assets for suite
        Args:
            suite: suite to get assets for
            files: Files to load
            **kwargs:

        Returns:
            Nested dictionaries in the structure
            experiment_id { simulation_id { files = content } } }
        """
        ret = dict()
        for exp in suite.experiments:
            e = self.platform.get_item(exp.uid, ItemType.EXPERIMENT)
            ret[str(exp.uid)] = self.platform.get_files(e, files, **kwargs)
        return ret
