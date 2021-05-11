"""idmtools local platform worker utils.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
from logging import getLogger
from sqlalchemy import func
from idmtools_platform_local.internals.data.job_status import JobStatus
from idmtools_platform_local.internals.workers.database import get_session, get_or_create
from idmtools_platform_local.status import Status

HOST_DATA_BIND = None
logger = getLogger(__name__)


def create_or_update_status(uuid, data_path=None, tags=None, status=Status.created, parent_uuid=None,
                            extra_details=None, session=None, autoclose=True, autocommit=True):
    """
    Update a jobs status in our db.

    Args:
        uuid: UUID to update
        data_path: Path to data
        tags: Tags to set
        status: status to set
        parent_uuid: Parent uuid
        extra_details: Extra details
        session: db session
        autoclose: Auto close session
        autocommit: Auto commit session

    Returns:
        None
    """
    if session is None:
        session = get_session()
    job_status: JobStatus = get_or_create(session, JobStatus, ['uuid'],
                                          uuid=uuid, data_path=data_path, tags=tags, status=status,
                                          parent_uuid=parent_uuid)
    if data_path is not None:
        job_status.data_path = data_path
    if tags is not None:
        job_status.tags = tags
    if status != job_status.status:
        job_status.status = status

    if extra_details is not None:
        job_status.extra_details = extra_details

    job_status.updated = func.now()
    session.add(job_status)
    if autocommit:
        session.commit()
    if autoclose:
        # close the sessions
        session.close()


def get_host_data_bind():
    """
    Get our HOST_DATA_BIND configuration.

    Returns:
        HOST_DATA_BIND configuration.
    """
    global HOST_DATA_BIND
    if HOST_DATA_BIND is None:
        data_bind = os.getenv('HOST_DATA_BIND', None)
        if data_bind is None:
            logger.error('HOST_DATA_BIND is not defined')
            raise ValueError("HOST_DATA_BIND is not set")
        logger.info(f'HOST_DATA_BIND parsing from {data_bind}')
        data_bind = data_bind.split(":")[0].strip()
        logger.info(f'HOST_DATA_BIND={data_bind}')
        HOST_DATA_BIND = data_bind
    return HOST_DATA_BIND
