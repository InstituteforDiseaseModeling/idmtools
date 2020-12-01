import json
from os import PathLike
from typing import Union, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from idmtools.core.interfaces.ientity import IEntity


def read_id_file(filename: Union[str, PathLike]):
    if isinstance(filename, PathLike):
        filename = str(filename)
    platform_block = None
    item_id = None
    item_type = None
    extra_args = None
    with open(filename, 'r') as id_in:
        item_id = id_in.read().strip()
        if "::" in item_id:
            parts = item_id.split("::")
            if len(parts) == 2:
                item_id, item_type = item_id.split("::")
            elif len(parts) == 3:
                item_id, item_type, platform_block = item_id.split("::")
            elif len(parts) == 4:
                item_id, item_type, platform_block, extra_args = item_id.split("::")
    return item_id, item_type, platform_block, extra_args


def write_id_file(filename: Union[str, PathLike], item: 'IEntity', save_platform: bool = False, platform_args: Dict = None):
    from idmtools.utils.json import IDMJSONEncoder
    if isinstance(filename, PathLike):
        filename = str(filename)
    with open(filename, 'w') as filename:
        filename.write(f'{item.id}')
        if save_platform and hasattr(item.platform, '_config_block'):
            filename.write(f"::{item.platform._config_block}::{item.item_type}")
            if platform_args:
                filename.write(json.dumps(platform_args, cls=IDMJSONEncoder))
