from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # The current platform
    from idmtools.entities.iplatform import IPlatform

current_platform_stack = []
CURRENT_PLATFORM: 'IPlatform' = None


def set_current_platform(platform: 'IPlatform'):
    global CURRENT_PLATFORM, current_platform_stack
    if CURRENT_PLATFORM and CURRENT_PLATFORM != platform:
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


def get_current_platform():
    return CURRENT_PLATFORM
