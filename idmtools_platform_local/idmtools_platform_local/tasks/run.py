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

    def perform(self, command: str, experiment_uuid: str, simulation_uuid: str) -> Status:
        """
        Runs our task and updates status

        Args:
            command: Command string to execute
            experiment_uuid: Experiment id of task
            simulation_uuid: Simulation id of task

        Returns:

        """
        # we only want to import this here so that clients don't need postgres/sqlalchemy packages
        from idmtools_platform_local.workers.utils import create_or_update_status
        from idmtools_platform_local.workers.data.job_status import JobStatus
        from idmtools_platform_local.workers.database import get_session

        # Get the current job
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

        # Add items to our system path
        sys.path.insert(0, simulation_path)
        sys.path.insert(0, asset_dir)
        # add to our details so it can be used for traceability downstream
        current_job.extra_details['system_path'] = sys.path
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f'System path: {sys.path}')

        return self.run_task(command, current_job, experiment_uuid, simulation_path, simulation_uuid)

    @staticmethod
    def run_task(command: str, current_job: JobStatus, experiment_uuid: str, simulation_path: str,
                 simulation_uuid: str) -> Status:
        """
        Executes the command and record its status in the database

        Args:
            command: command to run
            current_job: The JobStatus object to update
            experiment_uuid: experiment id
            simulation_path: Base root of the simulation execution path
            simulation_uuid: Simulation Id

        Returns:
            (Status) Status of the job. This is determine by the system return code of the process
        """
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
    def extract_status(experiment_uuid: str, process: subprocess.Popen, simulation_uuid) -> Status:
        """
        Extract status from a completed process
        Args:
            experiment_uuid: Id of experiment(needed to update job info)
            process: Process that has finished execution
            simulation_uuid: Simulation id of the task

        Returns:
            (Status) Status of the job
        """
        # Determine if the task succeeded or failed
        status = Status.done if process.returncode == 0 else Status.failed
        # If it failed, we should let the user know with a log message
        if status == Status.failed:
            # it is possible we killed the process through canceling. Let's check to be sure
            # before marking as canceled
            current_job: JobStatus = get_session().query(JobStatus). \
                filter(JobStatus.uuid == simulation_uuid, JobStatus.parent_uuid == experiment_uuid).first()
            if current_job.status == Status.canceled:
                status = Status.canceled
            logger.error('Simulation %s for Experiment %s failed with a return code of %s',
                         simulation_uuid, experiment_uuid, process.returncode)
        elif logger.isEnabledFor(logging.DEBUG):
            logging.debug('Simulation %s finished with status of %s', simulation_uuid, str(status))
        return status
