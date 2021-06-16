"""idmtools local platform task tools.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
import shlex
import stat
import subprocess
from logging import DEBUG
import sys
from idmtools.core import logging
from idmtools_platform_local.status import Status

logger = logging.getLogger(__name__)


def run_task(command: str, current_job: 'JobStatus', experiment_uuid: str, simulation_path: str,  # noqa: F821
             simulation_uuid: str) -> Status:
    """
    Executes the command and record its status in the database.

    Args:
        command: command to run
        current_job: The JobStatus object to update
        experiment_uuid: experiment id
        simulation_path: Base root of the simulation execution path
        simulation_uuid: Simulation Id

    Returns:
        (Status) Status of the job. This is determine by the system return code of the process
    """
    from idmtools_platform_local.internals.workers.utils import create_or_update_status
    # Open of Stdout and StdErr files that will be used to track input and output
    logger.debug(f"Simulation path {simulation_path}")
    with open(os.path.join(simulation_path, "StdOut.txt"), "w") as out, \
            open(os.path.join(simulation_path, "StdErr.txt"), "w") as err:
        try:
            logger.info('Executing %s from working directory %s', command, simulation_path)
            err.write(f"{command}\n")

            parts = shlex.split(command)
            fp = os.path.join(simulation_path, parts[0])
            if os.path.exists(fp):
                logger.debug(f"Ensuring Execute permission on file: {fp}")
                try:
                    st = os.stat(fp)
                    os.chmod(fp, st.st_mode | stat.S_IEXEC)
                except OSError:
                    if logger.isEnabledFor(DEBUG):
                        logger.debug(f"Could not set execute permission on {fp}. Falling back to executing with bash")
                    # most likely windows host. We can try to run it using another method
                    parts.insert(0, "/bin/bash")

            # Run our task
            p = subprocess.Popen(parts, cwd=simulation_path, shell=False, stdout=out, stderr=err)
            # store the pid in case we want to cancel later
            logger.info(f"Process id: {p.pid}")
            current_job.extra_details['pid'] = p.pid
            # Log that we have started this particular simulation
            create_or_update_status(simulation_uuid, status=Status.in_progress, extra_details=current_job.extra_details)
            p.wait()

            status = extract_status(experiment_uuid, p.returncode, simulation_uuid)

            # Update task with the final status
            create_or_update_status(simulation_uuid, status=status, extra_details=current_job.extra_details)
            return status
        except Exception as e:
            err.write(str(e))
            return Status.failed


def extract_status(experiment_uuid: str, return_code: int, simulation_uuid) -> Status:
    """
    Extract status from a completed process.

    Args:
        experiment_uuid: Id of experiment(needed to update job info)
        return_code: Return Code for item
        simulation_uuid: Simulation id of the task

    Returns:
        (Status) Status of the job
    """
    from idmtools_platform_local.internals.data.job_status import JobStatus
    from idmtools_platform_local.internals.workers.database import get_session
    # Determine if the task succeeded or failed
    status = Status.done if return_code == 0 else Status.failed
    # If it failed, we should let the user know with a log message
    if status == Status.failed:
        # it is possible we killed the process through canceling. Let's check to be sure
        # before marking as canceled
        current_job: JobStatus = get_session().query(JobStatus). \
            filter(JobStatus.uuid == simulation_uuid, JobStatus.parent_uuid == experiment_uuid).first()
        if current_job.status == Status.canceled:
            status = Status.canceled
        logger.error('Simulation %s for Experiment %s failed with a return code of %s',
                     simulation_uuid, experiment_uuid, return_code)
    elif logger.isEnabledFor(DEBUG):
        logger.debug('Simulation %s finished with status of %s', simulation_uuid, str(status))
    return status


def get_current_job(experiment_uuid, simulation_uuid, command):
    """
    Get our current job running.

    Args:
        experiment_uuid: Experiment to lookup
        simulation_uuid: Simulation to lookup
        command: Command we are running.

    Returns:
        Current job.
    """
    from idmtools_platform_local.internals.data.job_status import JobStatus
    from idmtools_platform_local.internals.workers.database import get_session
    # Get the current job
    current_job: JobStatus = get_session().query(JobStatus).filter(JobStatus.uuid == simulation_uuid, JobStatus.parent_uuid == experiment_uuid).first()
    if current_job.extra_details is None:
        logger.warning(f'{current_job.uuid} has no extra details')
        current_job.extra_details = dict()
    current_job.extra_details['command'] = command
    return current_job


def is_canceled(current_job):
    """
    Has the job been marked as canceled?

    Args:
        current_job: Job to check

    Returns:
        True if canceled, false otherwise.
    """
    from idmtools_platform_local.internals.workers.utils import create_or_update_status
    if current_job.status == Status.canceled:
        logger.info(f'Job {current_job.uuid} has been canceled')
        # update command extra_details. Useful in future for deletion
        create_or_update_status(current_job.uuid, extra_details=current_job.extra_details)
        return True
    return False


def execute_simulation(command, experiment_uuid, simulation_uuid):
    """
    Runs our task and updates status.

    Args:
        command: Command string to execute
        experiment_uuid: Experiment id of task
        simulation_uuid: Simulation id of task

    Returns:
        Task result
    """
    # we only want to import this here so that clients don't need postgres/sqlalchemy packages
    current_job = get_current_job(experiment_uuid, simulation_uuid, command)
    if is_canceled(current_job):
        return current_job.status
    # Define our simulation path and our root asset path
    simulation_path = os.path.join(os.getenv("DATA_PATH", "/data"), experiment_uuid, simulation_uuid)
    asset_dir = os.path.join(simulation_path, "Assets")
    # Add items to our system path
    sys.path.insert(0, simulation_path)
    sys.path.insert(0, asset_dir)
    # add to our details so it can be used for traceability downstream
    current_job.extra_details['system_path'] = sys.path
    if logger.isEnabledFor(DEBUG):
        logger.debug(f'System path: {sys.path}')
    return run_task(command, current_job, experiment_uuid, simulation_path, simulation_uuid)
