import os
import copy
import typing
import ast
from dataclasses import fields

if typing.TYPE_CHECKING:
    from idmtools.core import TPlatformClass

current_directory = os.path.dirname(os.path.realpath(__file__))
PLATFORM_ROOT = os.path.join(os.path.dirname(current_directory), "platforms")


class PlatformFactory:

    def __init__(self):
        self._builders = {}

    def register_type(self, platform_class: 'TPlatformClass'):
        """
        Register a platform to make it available for platform factory
        Args:
            platform_class: The definition of the platform class
        Returns: None
        """
        self._builders[platform_class.__module__] = platform_class

    def create(self, key, **kwargs) -> 'TPlatformt':
        """
        Create Platform with type identified by key
        Args:
            key: Platform module name
            **kwargs: inputs for Platform constructor
        Returns: created Platform
        """
        if key not in self._builders:
            try:
                # Try first to import it dynamically
                import importlib
                importlib.import_module(key)
            except:
                raise ValueError(f"The PlatformFactory could not create an platform of type {key}")

        builder = self._builders.get(key)

        # Add a temporary Property when creating Platform
        builder._FACTORY = property(lambda self: True)
        platform = builder(**kwargs)
        delattr(builder, '_FACTORY')

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

        def dynamically_import_module(platform_type):
            try:
                # Try first to import it dynamically
                import importlib
                imported_module = importlib.import_module(platform_type)
                return imported_module
            except:
                return None

        def retrieve_platform_module_name(platform_type):
            # 1 check if platform_type is module name and import form it
            imported_module = dynamically_import_module(platform_type)
            if imported_module:
                return imported_module

            # 2: try possible module names
            groups = PLATFORM_ROOT.split(os.sep)
            groups.append(platform_type)
            length = len(groups)
            for i in range(1, length):
                group = groups[-i:]
                module_name = ".".join(group)
                imported_module = dynamically_import_module(module_name)
                if imported_module:
                    return imported_module
            return None

        # if platform_type not in self._builders:
        imported_module = retrieve_platform_module_name(platform_type)
        if not imported_module:
            raise ValueError(f"The PlatformFactory could not create an platform of type {self.platform_type}")

        # Update field type
        platform_cls = self._builders.get(imported_module.__name__)
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
        return self.create(imported_module.__name__, **kwargs)


platform_factory = PlatformFactory()
