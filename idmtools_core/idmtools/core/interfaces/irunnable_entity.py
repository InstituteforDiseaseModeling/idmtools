from dataclasses import field
from inspect import signature
from logging import getLogger, DEBUG
from typing import List, Callable, TYPE_CHECKING
from abc import ABCMeta
if TYPE_CHECKING:
    from idmtools.entities.iplatform import IPlatform
    from idmtools.core.interfaces.iitem import IItem

runnable_hook = Callable[['IRunnableEntity', 'IPlatform'], None]
logger = getLogger(__name__)


class IRunnableEntity(metaclass=ABCMeta):
    __pre_run_hooks: List[runnable_hook] = field(default_factory=list, metadata={"md": True})
    __post_run_hooks: List[runnable_hook] = field(default_factory=list, metadata={"md": True})

    def pre_run(self, platform: 'IPlatform') -> None:
        """
        Called before the actual creation of the entity.

        Args:
            platform: Platform item is being created on

        Returns:

        """
        for hook in self.__pre_run_hooks:
            if logger.isEnabledFor(DEBUG):
                logger.debug(f'Calling pre-create hook named {hook.__name__ if hasattr(hook, "__name__") else str(hook)}')
            hook(self, platform)

    def post_run(self, platform: 'IPlatform') -> None:
        """
        Called after the actual creation of the entity.

        Args:
            platform: Platform item was created on

        Returns:

        """
        for hook in self.__post_run_hooks:
            if logger.isEnabledFor(DEBUG):
                logger.debug(f'Calling pre-create hook named {hook.__name__ if hasattr(hook, "__name__") else str(hook)}')
            hook(self, platform)

    def add_pre_run_hook(self, hook: runnable_hook):
        """
        Adds a hook function to be called before an item is ran

        Args:
            hook: Hook function. This should have two arguments, the item and the platform

        Returns:
            None
        """
        if len(signature(hook).parameters) != 2:
            raise ValueError("Pre Run hooks should have 2 arguments. The first argument will be the item, the second the platform")
        self.__pre_run_hooks.append(hook)

    def add_post_run_hook(self, hook: runnable_hook):
        """
        Adds a hook function to be called after an item has ran

        Args:
            hook: Hook function. This should have two arguments, the item and the platform

        Returns:
            None
        """
        if len(signature(hook).parameters) != 2:
            raise ValueError("Post Run hooks should have 2 arguments. The first argument will be the item, the second the platform")
        self.__post_run_hooks.append(hook)
