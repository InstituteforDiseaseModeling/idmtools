import logging
import os
import sys
from dramatiq import GenericActor
from idmtools_local.data import SimulationDatabase, Status, save_simulation_status, JobStatus

logger = logging.getLogger(__name__)


class RunTask(GenericActor):
    """
    Run the given `command` in the simulation folder.
    """
    class Meta:
        store_results = False
        max_retries = 0

    def perform(self, command: str, experiment_uuid: str, simulation_uuid: str):
        import subprocess
        simulation_path = os.path.join("/data", experiment_uuid, simulation_uuid)
        asset_dir = os.path.join("/data", experiment_uuid, "Assets")
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('Linking assets from %s to %s', asset_dir, os.path.join(simulation_path, 'Assets'))

        subprocess.call(['ln', '-s', asset_dir, os.path.join(simulation_path, 'Assets')])
        sys.path.insert(0, asset_dir)
        with open(os.path.join(simulation_path, "StdOut.txt"), "w") as out, open(os.path.join(simulation_path, "StdErr.txt"), "w") as err:
            import shlex
            logger.info('Executing %s from working directory %s', command, simulation_path)
            save_simulation_status(simulation_uuid, experiment_uuid, Status.in_progress)
            p = subprocess.Popen(shlex.split(command), cwd=simulation_path, shell=False, stdout=out,stderr=err)
            p.wait()
            status = Status.done if p.returncode == 0 else Status.failed
            if status == Status.failed:
                logger.error('Simulation %s for Experiment %s failed with a return code of %s',
                             simulation_uuid,  experiment_uuid, p.returncode)
            elif logger.isEnabledFor(logging.DEBUG):
                logging.debug('Simulation %s finished with status of %s', simulation_uuid, str(status))
            save_simulation_status(simulation_uuid, experiment_uuid, status=status)