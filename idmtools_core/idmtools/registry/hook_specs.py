from logging import getLogger
from typing import TYPE_CHECKING

from pluggy import HookspecMarker, HookimplMarker

if TYPE_CHECKING:
    from idmtools.core.interfaces.ientity import IEntity
    from idmtools.core.interfaces.irunnable_entity import IRunnableEntity
logger = getLogger(__name__)
user_logger = getLogger('user')

IDMTOOLS_HOOKS = 'IDMTOOLS_HOOKS'

function_hook_spec = HookspecMarker(IDMTOOLS_HOOKS)
function_hook_impl = HookimplMarker(IDMTOOLS_HOOKS)


@function_hook_spec
def idmtools_platform_pre_create_item(item: 'IEntity', **kwargs) -> 'IEntity':
    """
    This callback is called by the pre_create of each object type on a platform. An item can be a suite, workitem, simulation, asset collection or an experiment
    Args:
        item:
        **kwargs:

    Returns:

    """
    pass


@function_hook_spec
def idmtools_on_start():
    """
    Execute on startup when idmtools is first imported

    Returns:

    """
    pass


@function_hook_spec
def idmtools_runnable_on_done(item: 'IRunnableEntity', **kwargs):
    """
    Called when a runnable item finishes when it was being monitored

    Args:
        item: Item that was running
        **kwargs:

    Returns:

    """
    pass


@function_hook_spec
def idmtools_runnable_on_succeeded(item: 'IRunnableEntity', **kwargs):
    """
    Executed when a runnable item succeeds

    Args:
        item: Item that was running
        **kwargs:

    Returns:

    """
    pass


@function_hook_spec
def idmtools_runnable_on_failure(item: 'IRunnableEntity', **kwargs):
    """
    Executed when a runnable item fails

    Args:
        item: Item that was running
        **kwargs:

    Returns:

    """
    pass
