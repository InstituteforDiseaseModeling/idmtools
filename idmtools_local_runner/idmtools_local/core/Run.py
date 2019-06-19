import os
import sys
import uuid
from dramatiq import GenericActor
from idmtools_local.core.Data import ExperimentDatabase, SimulationDatabase, JobStatus, Status


class CreateExperimentTask(GenericActor):
    """
    Creates an experiment.
    - Create the folder
    - Also create the Assets folder to hold the experiments assets
    - Return the UUID of the newly created experiment
    """
    class Meta:
        store_results = True
        max_retries = 0

    def perform(self):
        import random
        import string
        uuid = ''.join(random.choice(string.digits + string.ascii_uppercase) for _ in range(5))

        # Save our experiment to our local platform db
        experiment_status: JobStatus = JobStatus(uid=uuid, data_path=os.path.join("/data", uuid))
        ExperimentDatabase.save(experiment_status)

        os.mkdir(os.path.join("/data", uuid))
        os.mkdir(os.path.join("/data", uuid, "Assets"))
        return uuid


class CreateSimulationTask(GenericActor):
    """
    Creates a simulation.
    - Create the simulation folder in the experiment_id parent folder
    - Returns the UUID of the newly created simulation folder
    """
    class Meta:
        store_results = True
        max_retries = 0

    def perform(self, experiment_id):
        import random
        import string
        uuid = ''.join(random.choice(string.digits + string.ascii_uppercase) for _ in range(5))

        simulation_status: JobStatus = JobStatus(uid=uuid, parent_uuid= experiment_id,
                                                 data_path=os.path.join("/data", experiment_id, uuid))
        SimulationDatabase.save(simulation_status)

        os.mkdir(os.path.join("/data", experiment_id, uuid))
        return uuid


class AddAssetTask(GenericActor):
    """
    Allows to add assets either to the experiment assets or the simulation assets
    - If simulation_id is None -> experiment asset
    - Else simulation asset
    """
    class Meta:
        store_results = True
        max_retries = 0

    def perform(self, experiment_id, filename, path=None, contents=None, simulation_id=None):
        path = os.path.join("/data", experiment_id, simulation_id or "Assets", path or "", filename)

        # Sometimes, workers tries to create the same folder at the same time, silence the exception
        if not os.path.exists(os.path.dirname(path)):
            try:
                os.mkdir(os.path.dirname(path))
            except:
                pass

        with open(path, "wb") as fp:
            fp.write(bytes(contents, 'utf-8'))


class RunTask(GenericActor):
    """
    Run the given `command` in the simulation folder.
    """
    class Meta:
        store_results = False
        max_retries = 0

    def perform(self, command, experiment_uuid: uuid.UUID, simulation_uuid: uuid.UUID):
        import subprocess
        simulation_path = os.path.join("/data", str(experiment_uuid), str(simulation_uuid))
        asset_dir = os.path.join("/data", str(experiment_uuid), "Assets")
        subprocess.call(['ln', '-s', asset_dir, os.path.join(simulation_path, 'Assets')])
        sys.path.insert(0, asset_dir)
        with open(os.path.join(simulation_path, "StdOut.txt"), "w") as out, open(os.path.join(simulation_path, "StdErr.txt"), "w") as err:

            import shlex
            p = subprocess.Popen(shlex.split(command), cwd=simulation_path, shell=False, stdout=out,stderr=err)
            sim_status = SimulationDatabase.retrieve(simulation_uuid)
            sim_status.status = Status.done if p.returncode == 0 else Status.failed
            SimulationDatabase.save(sim_status)