import os
import sys

from dramatiq import GenericActor


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
        max_retries = 5

    def perform(self, experiment_id):
        import random
        import string
        uuid = ''.join(random.choice(string.digits + string.ascii_uppercase) for _ in range(5))
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
        path = path or ""
        if simulation_id:
            path = os.path.join("/data", experiment_id, simulation_id, path, filename)
        else:
            path = os.path.join("/data", experiment_id, "Assets", path, filename)

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

    def perform(self, command, experiment_id, simulation_id):
        import subprocess
        simulation_path = os.path.join("/data", experiment_id, simulation_id)
        subprocess.call(['ln', '-s', os.path.join('/data', experiment_id, "Assets"), os.path.join(simulation_path, 'Assets')])
        sys.path.insert(0, os.path.join("/data", experiment_id, "Assets"))
        with open(os.path.join(simulation_path, "StdOut.txt"), "w") as out, open(os.path.join(simulation_path, "StdErr.txt"), "w") as err:

            import shlex
            p = subprocess.Popen(shlex.split(command), cwd=os.path.join("/data", experiment_id, simulation_id), shell=False, stdout=out,
                                 stderr=err)
