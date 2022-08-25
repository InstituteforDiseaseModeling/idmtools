from uuid import uuid4

from idmtools.core.interfaces.ientity import IEntity
from idmtools.registry.hook_specs import function_hook_impl


@function_hook_impl
def idmtools_generate_id(item: IEntity) -> str:
    """
    Generates an UUID

    Args:
        item:

    Returns:

    """
    return str(uuid4())
