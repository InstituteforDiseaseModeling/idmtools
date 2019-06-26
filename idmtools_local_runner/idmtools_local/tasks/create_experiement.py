import logging
import os
from dramatiq import GenericActor
from idmtools_local.config import DATA_PATH
from idmtools_local.data import JobStatus, ExperimentDatabase

logger = logging.getLogger(__name__)

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

    def perform(self, tags):
        import random
        import string
        uuid = ''.join(random.choice(string.digits + string.ascii_uppercase) for _ in range(5))
        if logger.isEnabledFor(logging.INFO):
            logger.debug('Creating experiment with id %s', uuid)

        # Save our experiment to our local platform db
        experiment_status: JobStatus = JobStatus(uid=uuid, data_path=os.path.join(DATA_PATH, uuid))
        ExperimentDatabase.save(experiment_status)

        asset_path = os.path.join(DATA_PATH, uuid, "Assets")
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('Creating asset directory for experiment %s at %s', uuid, asset_path)
        os.makedirs(asset_path, exist_ok=True)
        return uuid