"""
Utility method for writing and reading id files.

ID Files allow us to reload entities like Experiment, Simulations, AssetCollections, etc from a platform through files. This can
be enabling for workflows to chain steps together, or to self-document remote outputs in the local project directory.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import json
from os import PathLike
from typing import Union, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from idmtools.core.interfaces.ientity import IEntity


def read_id_file(filename: Union[str, PathLike]):
    """
    Reads an id from an id file.

    An id file is in the format of

    <id>::<item_type>::<config block>::<extra args>
    Args:
        filename:

    Returns:
        None
    """
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
    """
    Write an item as and id file.

    Args:
        filename: Filename to write file to
        item: Item to write out
        save_platform: When true, writes platform details to the file
        platform_args: Platform arguments to write out

    Returns:
        None
    """
    from idmtools.utils.json import IDMJSONEncoder
    if isinstance(filename, PathLike):
        filename = str(filename)
    with open(filename, 'w') as filename:
        filename.write(f'{item.id}::{item.item_type}')
        if save_platform and hasattr(item.platform, '_config_block'):
            filename.write(f"::{item.platform._config_block}")
            if platform_args:
                filename.write(json.dumps(platform_args, cls=IDMJSONEncoder))
