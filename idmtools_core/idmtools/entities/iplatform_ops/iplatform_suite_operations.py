from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Type, Any, List, Tuple, Dict, NoReturn
from uuid import UUID

from idmtools.entities import Suite


@dataclass
class IPlatformSuiteOperations(ABC):
    platform: 'IPlatform'
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

    def batch_create(self, suites: List[Suite], **kwargs) -> List[Tuple[Any, UUID]]:
        """
        Provides a method to batch create suites

        Args:
            suites: List of suites to create
            **kwargs:

        Returns:
            List of tuples containing the create object and id of item that was created
        """
        ret = []
        for suite in suites:
            ret.append(self.create(suite, **kwargs))
        return ret

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
        suite.post_creation()

    def create(self, suite: Suite, do_pre: bool = True, do_post: bool = True, **kwargs):
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
    def refresh_status(self, experiment: Suite):
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
            ret[exp.uid] = self.platform._experiments.get_assets(exp, files, **kwargs)
        return ret