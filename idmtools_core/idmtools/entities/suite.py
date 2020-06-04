from typing import NoReturn, Type
from abc import ABC
from dataclasses import dataclass, field
from idmtools.core.interfaces.inamed_entity import INamedEntity
from idmtools.core import ItemType, EntityContainer, NoPlatformException, EntityStatus


@dataclass(repr=False)
class Suite(INamedEntity, ABC):
    """
    Class that represents a generic suite (a collection of experiments).

    Args:
        experiments: The child items of this suite.
    """
    experiments: 'EntityContainer' = field(default_factory=lambda: EntityContainer(), compare=False,
                                           metadata={"pickle_ignore": True})

    item_type: 'ItemType' = field(default=ItemType.SUITE, compare=False, init=False)
    description: str = field(default=None, compare=False)

    def add_experiment(self, experiment: 'Experiment') -> 'NoReturn':  # noqa: F821
        """
        Add an experiment to the suite
        Args:
            experiment: the experiment to be linked to suite
        """
        ids = [exp.uid for exp in self.experiments]
        if experiment.uid in ids:
            return

        # Link the suite to the experiment. Assumes the experiment suite setter adds the experiment to the suite.
        experiment.suite = self

    def display(self):
        from idmtools.utils.display import display, suite_table_display
        display(self, suite_table_display)

    def pre_creation(self):
        pass

    def post_creation(self):
        pass

    def __repr__(self):
        return f"<Suite {self.uid} - {len(self.experiments)} experiments>"

    @property
    def done(self):
        """
        Return if an suite has finished executing

        Returns:
            True if all experiments have ran, False otherwise
        """
        return all([s.done for s in self.experiments])

    @property
    def succeeded(self) -> bool:
        """
        Return if an suite has succeeded. An suite is succeeded when all experiments have succeeded

        Returns:
            True if all experiments have succeeded, False otherwise
        """
        return all([s.succeeded for s in self.experiments])

    def run(self, wait_until_done: bool = False, platform: 'idmtools.entities.iplatform.IPlatform' = None,  # noqa: F821
            **run_opts) -> NoReturn:
        """
        Runs an experiment on a platform

        Args:
            wait_until_done: Whether we should wait on experiment to finish running as well. Defaults to False
            platform: Platform object to use. If not specified, we first check object for platform object then the current context
            **run_opts: Options to pass to the platform

        Returns:
            None
        """
        p = self.__check_for_platform_from_context(platform)
        p.run_items(self, **run_opts)
        if wait_until_done:
            self.wait()

    def __check_for_platform_from_context(self, platform) -> 'idmtools.entities.iplatform.IPlatform':  # noqa: F821
        """
        Try to determine platform of current object from self or current platform

        Args:
            platform: Passed in platform object

        Raises:
            NoPlatformException: when no platform is on current context
        Returns:
            Platform object
        """
        if self.platform is None:
            # check context for current platform
            if platform is None:
                from idmtools.core.platform_factory import current_platform
                if current_platform is None:
                    raise NoPlatformException("No Platform defined on object, in current context, or passed to run")
                platform = current_platform
            self.platform = platform
        return self.platform

    def wait(self, timeout: int = None, refresh_interval=None,
             platform: 'idmtools.entities.iplatform.IPlatform' = None):  # noqa: F821
        """
        Wait on an experiment to finish running

        Args:
            timeout: Timeout to wait
            refresh_interval: How often to refresh object
            platform: Platform. If not specified, we try to determine this from context

        Returns:

        """
        if self.status not in [EntityStatus.CREATED, EntityStatus.RUNNING]:
            raise ValueError("The experiment cannot be waited for if it is not in Running/Created state")
        opts = dict()
        if timeout:
            opts['timeout'] = timeout
        if refresh_interval:
            opts['refresh_interval'] = refresh_interval
        p = self.__check_for_platform_from_context(platform)
        p.wait_till_done_progress(self, **opts)


ISuiteClass = Type[Suite]
