from contextlib import contextmanager
from dataclasses import fields
from logging import getLogger
from typing import Dict, Any, TYPE_CHECKING

from idmtools.config import IdmConfigParser
from idmtools.core.context import set_current_platform, remove_current_platform
from idmtools.utils.entities import validate_user_inputs_against_dataclass

if TYPE_CHECKING:
    from idmtools.entities.iplatform import IPlatform

logger = getLogger(__name__)
user_logger = getLogger('user')


@contextmanager
def platform(*args, **kwds):
    logger.debug(f'Acquiring platform context with options: {str(*args)}')
    try:
        # check if we are already in a platform context and if so add to stack
        pl = Platform(*args, **kwds)
        set_current_platform(pl)
        yield pl
    finally:
        # Code to release resource, e.g.:
        logger.debug('Un-setting current platform context')
        remove_current_platform()


class Platform:

    def __new__(cls, block, missing_ok: bool = False, **kwargs):
        """
        Create a platform based on the block and all other inputs.

        Args:
            block: The INI configuration file block name.
            kwargs: User inputs may overwrite the entries in the block.

        Returns:
            The requested platform.

        Raises:
            ValueError if the block is None
        """
        global current_platform, current_platform_stack
        from idmtools.registry.platform_specification import PlatformPlugins

        if block is None:
            raise ValueError("Must have a valid Block name to create a Platform!")

        # Load all Platform plugins
        cls._platforms = PlatformPlugins().get_plugin_map()

        # Create Platform based on the given block
        platform = cls._create_from_block(block, missing_ok=missing_ok, **kwargs)
        set_current_platform(platform)
        return platform

    @classmethod
    def _validate_platform_type(cls, name):
        """
        Check if the requested platform exists.

        Args:
            name: The platform type.

        Returns:
            None

        Raise:
            ValueError: when the platform is of an unknown type
        """
        if name not in cls._platforms:
            raise ValueError(f"{name} is an unknown Platform Type. "
                             f"Supported platforms are {', '.join(cls._platforms.keys())}")

    @classmethod
    def _create_from_block(cls, block: str, missing_ok: bool = False, default_missing: Dict[str, Any] = None,
                           **kwargs) -> 'IPlatform':
        """
        Retrieve section entries from the INI configuration file by giving block.

        Args:
            block: The section name in the configuration file.
            missing_ok: Is it ok if section is missing(uses all default options)
            overrides: Optional override of parameters from the configuration file.

        Returns:
            A dictionary with entries from the block.
        """

        # Read block details
        try:
            section = IdmConfigParser.get_section(block, error=not missing_ok)
            if not section and missing_ok:
                # its possible our logger is not setup
                from idmtools.core.logging import setup_logging, listener
                if not listener:
                    setup_logging()
        except ValueError as e:
            if missing_ok:
                section = dict() if default_missing is None else default_missing
            else:
                raise e

        try:
            # Make sure block has type entry
            platform_type = section.pop('type')
        except KeyError:
            # try to use the block name as the type
            if missing_ok:
                user_logger.warning(
                    "You are specifying a platform without a configuration file or configuration block. Be sure you have supplied all required parameters for the Platform as this can result in unexpected behaviour. Running this way is only recommended for development mode. Instead, it is recommended you create an idmtools.ini to capture the config once you have tested and confirmed your configuration.")
                platform_type = block
            else:
                raise ValueError(
                    "When creating a Platform you must specify the type in the block. For example:\n    type = COMPS")

        # Make sure we support platform_type
        cls._validate_platform_type(platform_type)

        # Find the correct Platform type
        platform_spec = cls._platforms.get(platform_type)
        platform_cls = platform_spec.get_type()

        # Collect fields types
        fds = fields(platform_cls)
        field_name = [f.name for f in fds]
        field_type = {f.name: f.type for f in fds}

        # Make data to the requested type
        inputs = IdmConfigParser.retrieve_dict_config_block(field_type, section)

        # Make sure the user values have the requested type
        fs_kwargs = validate_user_inputs_against_dataclass(field_type, kwargs)  # noqa: F841

        # Update attr based on priority: #1 Code, #2 INI, #3 Default
        for fn in set(kwargs.keys()).intersection(set(field_name)):
            inputs[fn] = kwargs[fn]

        extra_kwargs = set(kwargs.keys()) - set(field_name)
        if len(extra_kwargs) > 0:
            field_not_used_display = [" - {} = {}".format(fn, kwargs[fn]) for fn in extra_kwargs]
            user_logger.warning("\n/!\\ WARNING: The following User Inputs are not used:")
            user_logger.warning("\n".join(field_not_used_display))

        # Display block info
        try:
            IdmConfigParser.display_config_block_details(block)
        except ValueError:
            if missing_ok:
                pass

        # Display not used fields of the block
        field_not_used = set(inputs.keys()) - set(field_type.keys())
        if len(field_not_used) > 0:
            field_not_used_display = [" - {} = {}".format(fn, inputs[fn]) for fn in field_not_used]
            user_logger.warning(f"\n[{block}]: /!\\ WARNING: the following Config Settings are not used when creating "
                                f"Platform:")
            user_logger.warning("\n".join(field_not_used_display))

        # Remove extra fields
        for f in field_not_used:
            inputs.pop(f)

        # Now create Platform using the data with the correct data types
        return platform_cls(**inputs)
