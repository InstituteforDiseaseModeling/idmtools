import os
from dramatiq import GenericActor, get_broker

from idmtools_local.config import DATA_PATH
from idmtools_local.core.Data import JobStatus, ExperimentDatabase


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
        print(__name__)
        import random
        import string
        uuid = ''.join(random.choice(string.digits + string.ascii_uppercase) for _ in range(5))

        # Save our experiment to our local platform db
        experiment_status: JobStatus = JobStatus(uid=uuid, data_path=os.path.join("/data", uuid))
        ExperimentDatabase.save(experiment_status)

        os.makedirs(os.path.join(DATA_PATH, uuid, "Assets"), exist_ok=True)
        return uuid

broker = get_broker()
broker.declare_actor(CreateExperimentTask)