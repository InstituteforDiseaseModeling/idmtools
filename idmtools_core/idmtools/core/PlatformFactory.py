import copy
import typing
import ast
from dataclasses import fields

if typing.TYPE_CHECKING:
    from idmtools.core import TPlatformClass


class PlatformFactory:

    def __init__(self):
        self._builders = {}

    def register_type(self, platform_class: 'TPlatformClass'):
        self._builders[platform_class.__module__] = platform_class

    def create(self, key, **kwargs) -> 'TPlatformt':
        if key not in self._builders:
            try:
                # Try first to import it dynamically
                import importlib
                importlib.import_module(key)
            except:
                raise ValueError(f"The PlatformFactory could not create an platform of type {key}")

        builder = self._builders.get(key)
        platform = builder(**kwargs)

        return platform

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

        # Update field type
        platform_cls = self._builders.get(platform_type)
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
        return self.create(platform_type, **kwargs)


platform_factory = PlatformFactory()
