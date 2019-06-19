import os
import sys

from dramatiq import GenericActor
from idmtools_local.data import SimulationDatabase, Status


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
        subprocess.call(['ln', '-s', asset_dir, os.path.join(simulation_path, 'Assets')])
        sys.path.insert(0, asset_dir)
        with open(os.path.join(simulation_path, "StdOut.txt"), "w") as out, open(os.path.join(simulation_path, "StdErr.txt"), "w") as err:

            import shlex
            p = subprocess.Popen(shlex.split(command), cwd=simulation_path, shell=False, stdout=out,stderr=err)
            sim_status: 'JobStatus' = SimulationDatabase.retrieve(simulation_uuid)
            sim_status.status = Status.done if p.returncode == 0 else Status.failed
            SimulationDatabase.save(sim_status)