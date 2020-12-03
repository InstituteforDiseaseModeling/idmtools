from logging import getLogger
from typing import TYPE_CHECKING

import pluggy

if TYPE_CHECKING:
    from idmtools.core.interfaces.ientity import IEntity

IDMTOOLS_HOOKS = 'IDMTOOLS_HOOKS'

pre_create_item_spec = pluggy.HookspecMarker(IDMTOOLS_HOOKS)
pre_create_item_impl = pluggy.HookimplMarker(IDMTOOLS_HOOKS)

logger = getLogger(__name__)
user_logger = getLogger('user')


@pre_create_item_spec
def idmtools_platform_pre_create_item(item: 'IEntity', **kwargs) -> 'IEntity':
    pass
