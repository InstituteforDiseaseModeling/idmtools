from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # The current platform
    from idmtools.entities.iplatform import IPlatform

current_platform_stack = []
current_platform: 'IPlatform' = None


def set_current_platform(platform: 'IPlatform'):
    global current_platform, current_platform_stack
    if current_platform and current_platform != platform:
        current_platform_stack.append(current_platform)
    current_platform = platform


def remove_current_platform():
    global current_platform, current_platform_stack
    old_current_platform = current_platform
    if len(current_platform_stack):
        new_platform = current_platform_stack.pop()
    else:
        new_platform = None
    del old_current_platform
    current_platform = new_platform
