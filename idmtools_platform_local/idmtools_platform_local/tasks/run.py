import logging
import os
import shlex
import sys
import subprocess
from dramatiq import GenericActor
from idmtools_platform_local.config import DATA_PATH
from idmtools_platform_local.status import Status
from idmtools_platform_local.workers.data.job_status import JobStatus
from idmtools_platform_local.workers.database import get_session
from idmtools_platform_local.workers.utils import create_or_update_status

logger = logging.getLogger(__name__)


class RunTask(GenericActor):
    """
    Run the given `command` in the simulation folder.
    """

    class Meta:
        store_results = False
        max_retries = 0

    def perform(self, command: str, experiment_uuid: str, simulation_uuid: str):
        # we only want to import this here so that clients don't need postgres/sqlalchemy packages
        from idmtools_platform_local.workers.utils import create_or_update_status
        from idmtools_platform_local.workers.data.job_status import JobStatus
        from idmtools_platform_local.workers.database import get_session

        # Check if the job has been canceled
        current_job: JobStatus = get_session().query(JobStatus). \
            filter(JobStatus.uuid == simulation_uuid, JobStatus.parent_uuid == experiment_uuid).first()

        current_job.extra_details['command'] = command

        if current_job.status == Status.canceled:
            logger.info(f'Job {current_job.uuid} has been canceled')
            # update command extra_details. Useful in future for deletion
            create_or_update_status(simulation_uuid, extra_details=current_job.extra_details)
            return current_job.status

        # Define our simulation path and our root asset path
        simulation_path = os.path.join(DATA_PATH, experiment_uuid, simulation_uuid)
        asset_dir = os.path.join(simulation_path, "Assets")

        sys.path.insert(0, simulation_path)
        sys.path.insert(0, asset_dir)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f'System path: {sys.path}')

        return self.run_task(command, current_job, experiment_uuid, simulation_path, simulation_uuid)

    @staticmethod
    def run_task(command, current_job, experiment_uuid, simulation_path, simulation_uuid):
        # Open of Stdout and StdErr files that will be used to track input and output
        with open(os.path.join(simulation_path, "StdOut.txt"), "w") as out, \
                open(os.path.join(simulation_path, "StdErr.txt"), "w") as err:
            logger.info('Executing %s from working directory %s', command, simulation_path)

            # Run our task
            p = subprocess.Popen(shlex.split(command), cwd=simulation_path, shell=False, stdout=out, stderr=err)
            # store the pid in case we want to cancel later
            current_job.extra_details['pid'] = p.pid
            # Log that we have started this particular simulation
            create_or_update_status(simulation_uuid, status=Status.in_progress, extra_details=current_job.extra_details)
            p.wait()

            status = RunTask.extract_status(experiment_uuid, p, simulation_uuid)

            # Update task with the final status
            create_or_update_status(simulation_uuid, status=status, extra_details=current_job.extra_details)
            return status

    @staticmethod
    def extract_status(experiment_uuid, p, simulation_uuid):
        # Determine if the task succeeded or failed
        status = Status.done if p.returncode == 0 else Status.failed
        # If it failed, we should let the user know with a log message
        if status == Status.failed:
            # it is possible we killed the process through canceling. Let's check to be sure
            # before marking as canceled
            current_job: JobStatus = get_session().query(JobStatus). \
                filter(JobStatus.uuid == simulation_uuid, JobStatus.parent_uuid == experiment_uuid).first()
            if current_job.status == Status.canceled:
                status = Status.canceled
            logger.error('Simulation %s for Experiment %s failed with a return code of %s',
                         simulation_uuid, experiment_uuid, p.returncode)
        elif logger.isEnabledFor(logging.DEBUG):
            logging.debug('Simulation %s finished with status of %s', simulation_uuid, str(status))
        return status
