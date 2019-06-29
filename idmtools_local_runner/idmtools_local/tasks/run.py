import logging
import os
import shlex
import sys
import subprocess
from dramatiq import GenericActor

from idmtools_local.config import DATA_PATH

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
        from idmtools_local.utils import create_or_update_status
        from idmtools_local.data.job_status import Status

        # Define our simulation path and our root asset path
        simulation_path = os.path.join(DATA_PATH, experiment_uuid, simulation_uuid)
        asset_dir = os.path.join(DATA_PATH, experiment_uuid, "Assets")

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('Linking assets from %s to %s', asset_dir, os.path.join(simulation_path, 'Assets'))

        # Link in our asset directory and then add to our system path so any executing programs can see
        # the assets using relative paths.. ie ./Assest/tmp.xt
        os.symlink(asset_dir, os.path.join(simulation_path, 'Assets'))
        sys.path.insert(0, asset_dir)

        # Open of Stdout and StdErr files that will be used to track input and output
        with open(os.path.join(simulation_path, "StdOut.txt"), "w") as out, open(os.path.join(simulation_path, "StdErr.txt"), "w") as err:
            logger.info('Executing %s from working directory %s', command, simulation_path)

            # Log that we have started this particular simulation
            create_or_update_status(simulation_uuid, status=Status.in_progress)

            # Run our task
            p = subprocess.Popen(shlex.split(command), cwd=simulation_path, shell=False, stdout=out,stderr=err)
            p.wait()

            # Determine if the task succeeded or failed
            status = Status.done if p.returncode == 0 else Status.failed

            # If it failed, we should let the user know with a log message
            if status == Status.failed:
                logger.error('Simulation %s for Experiment %s failed with a return code of %s',
                             simulation_uuid,  experiment_uuid, p.returncode)
            elif logger.isEnabledFor(logging.DEBUG):
                logging.debug('Simulation %s finished with status of %s', simulation_uuid, str(status))

            # Update task with the final status
            create_or_update_status(simulation_uuid, status=status)