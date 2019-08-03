import copy
import typing
import ast
from dataclasses import fields

from idmtools.utils.decorators import SingletonDecorator, LoadOnCallSingletonDecorator

if typing.TYPE_CHECKING:
    from idmtools.core.types import TPlatform


# TODO: Update to use plugin manager

class PlatformFactory:

    def __init__(self):
        from idmtools.registry.PlatformSpecification import PlatformPlugins
        self._platforms = PlatformPlugins().get_plugin_map()

    def create(self, key, **kwargs) -> 'TPlatform':
        """
        Create Platform with type identified by key
        Args:
            key: Platform module name
            **kwargs: inputs for Platform constructor
        Returns: created Platform
        """
        self._validate_platform_type(key)
        builder = self._platforms.get(key)
        return builder.get(kwargs)

    def _validate_platform_type(self, name):
        if name not in self._platforms:
            raise ValueError(f"{name} is an unknown Platform Type."
                             f"Supported platforms are {','.join(self._platforms.keys())}")

    def create_from_block(self, block):
        """
        Retrieve section entries from config file by giving block
        Args:
            block: the section name in config file
        Returns: dict with entries from the block
        """
        from idmtools.config import IdmConfigParser
        section = IdmConfigParser.get_block(block)
        platform_type = section.pop('type')
        self._validate_platform_type(platform_type)
        platform_spec = self._platforms.get(platform_type)

        # Update fields types
        platform_cls = platform_spec.get_type()
        fds = fields(platform_cls)
        field_type = {f.name: f.type for f in fds}

        kwargs = copy.deepcopy(section)
        fs = set(field_type.keys()).intersection(set(section.keys()))
        for fn in fs:
            ft = field_type[fn]
            if ft in (int, float, str):
                kwargs[fn] = ft(section[fn])
            elif ft is bool:
                kwargs[fn] = ast.literal_eval(section[fn])

        # Display not used fields from config
        field_not_used = set(kwargs.keys()) - set(field_type.keys())
        if len(field_not_used) > 0:
            field_not_used_display = [" - {} = {}".format(fn, kwargs[fn]) for fn in field_not_used]
            print(f"[{block}]: the following Config Settings are not used:")
            print("\n".join(field_not_used_display))

        # Remove extra fields
        for f in field_not_used:
            kwargs.pop(f)

        # Now create Platform using the data with the correct data types
        # Add a temporary Property when creating Platform
        platform_cls._FACTORY = property(lambda self: True)
        platform = platform_cls(**kwargs)
        delattr(platform_cls, '_FACTORY')

        return platform


PlatformFactory = LoadOnCallSingletonDecorator(PlatformFactory)
