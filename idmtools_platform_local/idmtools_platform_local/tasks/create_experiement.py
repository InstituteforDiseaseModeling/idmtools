import logging
import os
import random
import string
from dramatiq import GenericActor
from idmtools_platform_local.config import DATA_PATH

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

    def perform(self, tags, simulation_type):
        # we only want to import this here so that clients don't need postgres/sqlalchemy packages
        from idmtools_platform_local.workers.utils import create_or_update_status
        uuid = ''.join(random.choice(string.digits + string.ascii_uppercase) for _ in range(8))
        if logger.isEnabledFor(logging.INFO):
            logger.debug('Creating experiment with id %s', uuid)

        data_path = os.path.join(DATA_PATH, uuid)

        # Update the database with experiment
        create_or_update_status(uuid, data_path, tags, extra_details=dict(simulation_type=simulation_type))

        asset_path = os.path.join(data_path, "Assets")
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('Creating asset directory for experiment %s at %s', uuid, asset_path)
        os.makedirs(asset_path, exist_ok=True)
        return uuid
