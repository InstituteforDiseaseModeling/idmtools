from logging import getLogger
from typing import TYPE_CHECKING

logger = getLogger(__name__)
if TYPE_CHECKING:  # pragma: no cover
    # The current platform
    from idmtools.entities.iplatform import IPlatform

current_platform_stack = []
CURRENT_PLATFORM: 'IPlatform' = None


def set_current_platform(platform: 'IPlatform'):
    global CURRENT_PLATFORM, current_platform_stack
    if CURRENT_PLATFORM and CURRENT_PLATFORM != platform and platform not in current_platform_stack:
        current_platform_stack.append(CURRENT_PLATFORM)
    CURRENT_PLATFORM = platform


def remove_current_platform():
    global CURRENT_PLATFORM, current_platform_stack
    old_current_platform = CURRENT_PLATFORM
    if len(current_platform_stack):
        new_platform = current_platform_stack.pop()
    else:
        new_platform = None
    del old_current_platform
    CURRENT_PLATFORM = new_platform


def clear_context():
    """
    Clear all platforms from context
    """
    global CURRENT_PLATFORM, current_platform_stack
    old_current_platform = CURRENT_PLATFORM
    CURRENT_PLATFORM = None
    current_platform_stack.clear()
    del old_current_platform


def get_current_platform() -> 'IPlatform':
    """
    Get current platform
    """
    return CURRENT_PLATFORM
