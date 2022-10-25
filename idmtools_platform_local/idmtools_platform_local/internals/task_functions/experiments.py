"""idmtools local platform experiment task tools.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import logging
import os
import random
import string
from psycopg2._psycopg import IntegrityError
from typing import Dict, Any
import backoff

EXPERIMENT_ID_LENGTH = 8
logger = logging.getLogger(__name__)


@backoff.on_exception(backoff.constant, IntegrityError, max_tries=3, interval=0.02, jitter=None)
def get_uuid_and_data_path(tags, extra_details):
    """
    Get a uuid and a path to write experiment data to.

    Args:
        tags: Tags to use
        extra_details: Extra details for item.

    Returns:
        Data path and uuid
    """
    # we only want to import this here so that clients don't need postgres/sqlalchemy packages
    from idmtools_platform_local.internals.workers.utils import create_or_update_status
    uuid = ''.join(random.choice(string.digits + string.ascii_uppercase) for _ in range(EXPERIMENT_ID_LENGTH))
    if logger.isEnabledFor(logging.INFO):
        logger.debug('Creating experiment with id %s', uuid)
    # Update the database with experiment
    data_path = os.path.join(os.getenv("DATA_PATH", "/data"), uuid)
    create_or_update_status(uuid, data_path, tags, extra_details=extra_details)
    return data_path, uuid


def create_experiment(tags: Dict[str, Any], extra_details: Dict[str, Any] = None) -> str:
    """
    Creates an experiment.

        - Create the folder
        - Also create the Assets folder to hold the experiments assets
        - Return the UUID of the newly created experiment

    Args:
        tags (TTags): Tags for the experiment to be created
        extra_details: Metadata for item

    Returns:
        (str) Id of created experiment
    """
    retries = 0
    data_path = None
    uuid = None
    if extra_details is None:
        extra_details = dict()
    while retries <= 3:
        try:
            data_path, uuid = get_uuid_and_data_path(tags, extra_details)
            break
        except IntegrityError:
            retries += 1
    if retries > 3:
        raise ValueError("Could not save experiment id because of conflicting ids")

    asset_path = os.path.join(data_path, "Assets")
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug('Creating asset directory for experiment %s at %s', uuid, asset_path)
    os.makedirs(asset_path, exist_ok=True)
    return uuid
