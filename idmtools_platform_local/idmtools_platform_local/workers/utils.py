from idmtools_platform_local.workers.database import get_or_create, get_session
from idmtools_platform_local.workers.data.job_status import JobStatus, Status


def create_or_update_status(uuid, data_path=None, tags=None, status=Status.created, parent_uuid=None,
                            extra_details=None, session=None, autoclose=True):
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
    session.add(job_status)
    session.commit()
    # close the sessions
    if autoclose:
        session.close()
