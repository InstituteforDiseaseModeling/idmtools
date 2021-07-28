"""idmtools local platform simulation task tools.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import logging
import os
from typing import Dict, Tuple, Any
from uuid import UUID
import backoff
from psycopg2._psycopg import IntegrityError
import random
import string

logger = logging.getLogger(__name__)
SIM_ID_LENGTH = 8


@backoff.on_exception(backoff.constant, IntegrityError, max_tries=3, interval=0.02, jitter=None)
def get_uuid_and_data_path(experiment_id, session, tags, extra_details: Dict[str, any]):
    """
    Get the simulation uuid and data path.

    Args:
        experiment_id: Experiment id
        session: db session
        tags: Tags to set on item
        extra_details: Extra details to store.

    Returns:
        uuid and data path
    """
    from idmtools_platform_local.internals.workers.utils import create_or_update_status
    uuid = ''.join(random.choice(string.digits + string.ascii_uppercase) for _ in range(SIM_ID_LENGTH))
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug('Creating simulation %s for experiment %s', uuid, experiment_id)
    # create data path
    data_path = os.path.join(os.getenv("DATA_PATH", "/data"), experiment_id, uuid)
    # store info in db to ensure id is unique
    create_or_update_status(uuid, data_path, tags, parent_uuid=experiment_id, session=session,
                            autoclose=session is None, extra_details=extra_details)
    return uuid, data_path


def create_simulation(experiment_id: str, tags_and_extra_details: Tuple[Dict[str, Any], Dict[str, any]],
                      session=None) -> UUID:
    """
    Creates the simulation.

    We pass tags and extra details as tuple to make batching easier and overlap with the normal create.

    Args:
        experiment_id: Experiment id
        tags_and_extra_details: Tuple contains tags dict and then dict of extra details(metadata(
        session:

    Returns:
        UUid of created sim
    """
    # we only want to import this here so that clients don't need postgres/sqlalchemy packages

    tags, extra_details = tags_and_extra_details
    uuid, data_path = get_uuid_and_data_path(experiment_id, session, tags, extra_details)
    # Ensure data directories exist
    os.makedirs(data_path, exist_ok=True)

    # Define our simulation path and our root asset path
    simulation_path = os.path.join(os.getenv("DATA_PATH", "/data"), experiment_id, uuid)
    asset_dir = os.path.join(os.getenv("DATA_PATH", "/data"), experiment_id, "Assets")

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug('Linking assets from %s to %s', asset_dir, os.path.join(simulation_path, 'Assets'))

    # Link in our asset directory and then add to our system path so any executing programs can see
    # the assets using relative paths.. ie ./Asset/tmp.txt
    os.symlink(asset_dir, os.path.join(simulation_path, 'Assets'))

    return uuid
