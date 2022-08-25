"""
Define a id generator plugin that generates ids in sequence by item type.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import json
from logging import getLogger, INFO
from pathlib import Path

from idmtools import IdmConfigParser
from idmtools.core.interfaces.ientity import IEntity
from idmtools.registry.hook_specs import function_hook_impl

logger = getLogger(__name__)


def load_existing_sequence_data(sequence_file):
    data = dict()

    if Path(sequence_file).exists():
        with open(sequence_file, 'r') as file:
            data = json.load(file)
    return data


@function_hook_impl
def idmtools_generate_id(item: IEntity) -> str:
    """
    Generates an UUID

    Args:
        item: IEntity using the item_sequence plugin

    Returns:
        ID for the respective item, based on the formatting defined in the id_format_str (in .ini config file)

    """
    sequence_file = Path(IdmConfigParser.get_option("item_sequence", "sequence_file", 'item_sequences.json')).expanduser()
    id_format_str = IdmConfigParser.get_option("item_sequence", "id_format_str", '{item_name}{data[item_name]:07d}')
    data = load_existing_sequence_data(sequence_file)

    item_name = str(item.item_type if hasattr(item, 'item_type') else "Unknown")
    if item_name in data:
        data[item_name] += 1
    else:
        if logger.isEnabledFor(INFO):
            logger.info(f"Starting sequence for {item_name} at 0")
        data[item_name] = 0
    if not sequence_file.parent.exists():
        if logger.isEnabledFor(INFO):
            logger.info(f"Creating {sequence_file.parent}")
        sequence_file.parent.mkdir(exist_ok=True, parents=True)
    with open(sequence_file, 'w') as f:
        json.dump(data, f)
    return eval("f'" + id_format_str + "'")
