import ast
import copy
import typing
from dataclasses import fields
from idmtools.config import IdmConfigParser

if typing.TYPE_CHECKING:
    from idmtools.core.types import TPlatform


class Platform:

    def __new__(cls, block, **kwargs):
        """
        Create a platform based on the block and all other inputs
        Args:
            block: idmtools.ini block name
            kwargs: user inputs may overwrite the entries in the block
        Returns: requested Platform
        """
        from idmtools.registry.PlatformSpecification import PlatformPlugins

        if block is None:
            raise ValueError("Must have a valid Block name to create a Platform!")

        # Load all Platform plugins
        cls._platforms = PlatformPlugins().get_plugin_map()

        # Create Platform based on the given block
        platform = cls._create_from_block(block, **kwargs)
        return platform

    @classmethod
    def _validate_platform_type(cls, name):
        """
        Check if requested platform exists
        Args:
            name: Platform type
        Returns: True/False
        """
        if name not in cls._platforms:
            raise ValueError(f"{name} is an unknown Platform Type. "
                             f"Supported platforms are {', '.join(cls._platforms.keys())}")

    @classmethod
    def _create_from_block(cls, block: str, **kwargs):
        """
        Retrieve section entries from config file by giving block
        Args:
            block: the section name in config file
            kwargs: inputs may override block values
        Returns: platform with the type provided in the block
        """

        # Read block details
        section = IdmConfigParser.get_block(block)

        try:
            # Make sure block has type entry
            platform_type = section.pop('type')
        except KeyError:
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
        inputs = copy.deepcopy(section)
        fs = set(field_type.keys()).intersection(set(section.keys()))
        for fn in fs:
            ft = field_type[fn]
            if ft in (int, float, str):
                inputs[fn] = ft(section[fn])
            elif ft is bool:
                inputs[fn] = ast.literal_eval(section[fn])

        # Make sure the user values have the requested type
        fs_kwargs = set(field_type.keys()).intersection(set(kwargs.keys()))
        for fn in fs_kwargs:
            ft = field_type[fn]
            if ft in (int, float, str):
                kwargs[fn] = ft(kwargs[fn]) if kwargs[fn] is not None else kwargs[fn]
            elif ft is bool:
                kwargs[fn] = ast.literal_eval(kwargs[fn]) if isinstance(kwargs[fn], str) else kwargs[fn]

        # Update attr based on priority: #1 Code, #2 INI, #3 Default
        for fn in set(kwargs.keys()).intersection(set(field_name)):
            inputs[fn] = kwargs[fn]

        extra_kwargs = set(kwargs.keys()) - set(field_name)
        if len(extra_kwargs) > 0:
            field_not_used_display = [" - {} = {}".format(fn, kwargs[fn]) for fn in extra_kwargs]
            print(f"\n/!\\ WARNING: The following User Inputs are not used:")
            print("\n".join(field_not_used_display))

        # Display block info
        IdmConfigParser.display_config_block_details(block)

        # Display not used fields of the block
        field_not_used = set(inputs.keys()) - set(field_type.keys())
        if len(field_not_used) > 0:
            field_not_used_display = [" - {} = {}".format(fn, inputs[fn]) for fn in field_not_used]
            print(f"\n[{block}]: /!\\ WARNING: the following Config Settings are not used:")
            print("\n".join(field_not_used_display))

        # Remove extra fields
        for f in field_not_used:
            inputs.pop(f)

        # Now create Platform using the data with the correct data types
        return platform_cls(**inputs)
