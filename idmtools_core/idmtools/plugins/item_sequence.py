"""
Defines a id generator plugin that generates ids in sequence by item type.
To configure, set 'id_generator' in .ini configuration file to 'item_sequence':
[COMMON]
id_generator = item_sequence

You can also customize the sequence_file that stores the sequential ids per item type
as well as the id format using the following parameters in the .ini configuration file:
[item_sequence]
sequence_file = <file_name>.json    ex: index.json
id_format_str = <custom_str_format>     ex: {item_name}{data[item_name]:06d}

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import shutil
import json
import time
import warnings
from functools import lru_cache
from json import JSONDecodeError
from logging import getLogger, INFO, DEBUG
from pathlib import Path
from random import randint
import jinja2
from filelock import FileLock
from idmtools import IdmConfigParser
from idmtools.core import IDMTOOLS_USER_HOME
from idmtools.registry.hook_specs import function_hook_impl
from idmtools.core.interfaces.ientity import IEntity

logger = getLogger(__name__)
SEQUENCE_FILE_DEFAULT_PATH = IDMTOOLS_USER_HOME.joinpath("itemsequence", "index.json")


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
            except JSONDecodeError as e:
                if logger.isEnabledFor(DEBUG):
                    logger.error("Trouble loading data from sequence_file. Verify that designated sequence_file is "
                                 "not corrupted or deleted.")
                    logger.exception(e)
                return dict()
    return data


@lru_cache(maxsize=None)
def get_plugin_config():
    """
    Retrieves the sequence file and format string (for id generation) from the .ini config file.

    Returns:
        sequence_file: specified json file in .ini config in which id generator keeps track of sequential id's
        id_format_str: string specified in .ini config by which id's are formatted when assigned to sequential items
    """
    warnings.warn('This feature is currently under development')
    sequence_file = Path(IdmConfigParser.get_option("item_sequence", "sequence_file", SEQUENCE_FILE_DEFAULT_PATH))
    id_format_str = IdmConfigParser.get_option("item_sequence", "id_format_str", None)
    return sequence_file, id_format_str


@lru_cache(maxsize=None)
def _get_template(id_format_str):
    """
    Get our jinja template. Cache this to reduce work.

    Args:
        id_format_str: Format string

    Returns:
        Jinja2 template
    """
    environment = jinja2.Environment()
    template = environment.from_string(id_format_str)
    return template


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
    data = dict()
    item_name = str(item.item_type if hasattr(item, 'item_type') else "Unknown")
    while attempts < max_tries:
        try:
            lock = FileLock(f"{sequence_file}.lock", timeout=1)
            with lock:
                data = load_existing_sequence_data(sequence_file)

                if item_name in data:
                    data[item_name] += 1
                else:
                    if logger.isEnabledFor(INFO):
                        logger.info(f"Starting sequence for {item_name} at 0")
                    data[item_name] = 0

                with open(sequence_file, 'w') as f:
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
    if id_format_str:
        return _get_template(id_format_str).render(**locals())
    else:
        return f'{item_name}{data[item_name]:07d}'


@function_hook_impl
def idmtools_platform_post_run(item: 'IEntity', kwargs) -> 'IEntity':
    """
    Do a backup of sequence file if it is the id generator.

    Args:
        item: Item(we only save on experiments/suites at the moment)
        kwargs: extra args

    Returns:
        None
    """
    from idmtools.entities.suite import Suite
    from idmtools.entities.experiment import Experiment
    if IdmConfigParser.get_option(None, "id_generator", "uuid").lower() == "item_sequence":
        if isinstance(item, (Suite, Experiment)):
            sequence_file = Path(IdmConfigParser.get_option("item_sequence", "sequence_file", SEQUENCE_FILE_DEFAULT_PATH))
            sequence_file_bk = f'{sequence_file}.bak'
            shutil.copy(sequence_file, sequence_file_bk)
