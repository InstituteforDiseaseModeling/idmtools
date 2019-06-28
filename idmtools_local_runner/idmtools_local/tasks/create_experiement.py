import logging
import os
from dramatiq import GenericActor
from idmtools_local.config import DATA_PATH
from idmtools_local.utils import create_or_update_status

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
        uuid = ''.join(random.choice(string.digits + string.ascii_uppercase) for _ in range(8))
        if logger.isEnabledFor(logging.INFO):
            logger.debug('Creating experiment with id %s', uuid)

        data_path = os.path.join(DATA_PATH, uuid)

        # Update the database with experiment
        create_or_update_status(uuid, data_path, tags)

        asset_path = os.path.join(data_path, "Assets")
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('Creating asset directory for experiment %s at %s', uuid, asset_path)
        os.makedirs(asset_path, exist_ok=True)
        return uuid

