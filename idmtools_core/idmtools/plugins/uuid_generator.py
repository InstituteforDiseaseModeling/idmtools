"""
Defines a uuid generator plugin that generates an item id as a uuid.
To configure, set 'id_generator' in .ini configuration file to 'uuid':
[COMMON]
id_generator = uuid

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from uuid import uuid4
from idmtools.core.interfaces.ientity import IEntity
from idmtools.registry.hook_specs import function_hook_impl


@function_hook_impl
def idmtools_generate_id(item: IEntity) -> str:
    """
    Generates a UUID.

    Args:
        item: respective item for which we are generating an id

    Returns:
        uuid str as item id
    """
    return str(uuid4())
