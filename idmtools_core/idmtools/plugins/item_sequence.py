"""
Defines a id generator plugin that generates ids in sequence by item type.
To configure, set 'id_generator' in .ini configuration file to 'item_sequence':
[COMMON]
id_generator = item_sequence

You can also customize the sequence_file that stores the sequential ids per item type
as well as the id format using the following parameters in the .ini configuration file:
[item_sequence]
sequence_file = <file_name>.json    ex: item_sequences.json
id_format_str = <custom_str_format>     ex: {item_name}{data[item_name]:06d}

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import json
import time
from functools import cache
from json import JSONDecodeError
from logging import getLogger, INFO, DEBUG
from pathlib import Path
from random import randint

from filelock import FileLock
from idmtools import IdmConfigParser
from idmtools.core.interfaces.ientity import IEntity
from idmtools.registry.hook_specs import function_hook_impl

logger = getLogger(__name__)


def load_existing_sequence_data(sequence_file):
    """
    Loads item sequence data from sequence_file into a dictionary.

    Args:
        sequence_file: File that user has indicated to store the sequential ids of items

    Returns:
        Data loaded from sequence_file as a dictionary
    """
    data = dict()

    if Path(sequence_file).exists():
        with open(sequence_file, 'r') as file:
            try:
                data = json.load(file)
            except JSONDecodeError:
                return dict()
    return data


@cache
def get_plugin_config():
    """
    Retrieves the sequence file and format string (for id generation) from the .ini config file.

    Returns:
        sequence_file: specified json file in .ini config in which id generator keeps track of sequential id's
        id_format_str: string specified in .ini config by which id's are formatted when assigned to sequential items
    """
    sequence_file = Path(IdmConfigParser.get_option("item_sequence", "sequence_file", 'item_sequences.json')).expanduser()
    id_format_str = IdmConfigParser.get_option("item_sequence", "id_format_str", '{item_name}{data[item_name]:07d}')
    return sequence_file, id_format_str


@function_hook_impl
def idmtools_generate_id(item: IEntity) -> str:
    """
    Generates a UUID.

    Args:
        item: IEntity using the item_sequence plugin

    Returns:
        ID for the respective item, based on the formatting defined in the id_format_str (in .ini config file)

    """
    sequence_file, id_format_str = get_plugin_config()
    # we can check for existence here since it should only not exist when a new sequence is started
    if not sequence_file.parent.exists():
        if logger.isEnabledFor(INFO):
            logger.info(f"Creating {sequence_file.parent}")
        sequence_file.parent.mkdir(exist_ok=True, parents=True)

    max_tries = 100
    attempts = 0
    while attempts < max_tries:
        try:
            lock = FileLock(sequence_file, timeout=1)
            with lock:
                with open(sequence_file, 'w') as f:
                    data = load_existing_sequence_data(sequence_file)

                    item_name = str(item.item_type if hasattr(item, 'item_type') else "Unknown")
                    if item_name in data:
                        data[item_name] += 1
                    else:
                        if logger.isEnabledFor(INFO):
                            logger.info(f"Starting sequence for {item_name} at 0")
                        data[item_name] = 0

                    json.dump(data, f)
                    break
        except Exception as e:
            attempts += 1
            if attempts >= max_tries:
                raise e
            # We had an issue generating sequence. We assume
            if logger.isEnabledFor(DEBUG):
                logger.error("Trouble generating sequence.")
                logger.exception(e)
            time.sleep(randint(1, 4) * 0.01)
    return eval("f'" + id_format_str + "'")
