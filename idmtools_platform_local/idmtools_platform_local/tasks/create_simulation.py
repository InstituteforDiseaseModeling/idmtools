import logging
import os
from dramatiq import GenericActor

from idmtools.core import TTags
from idmtools_platform_local.config import DATA_PATH
import random
import string

logger = logging.getLogger(__name__)


class CreateSimulationTask(GenericActor):
    """
    Creates a simulation.
    - Create the simulation folder in the experiment_id parent folder
    - Returns the UUID of the newly created simulation folder
    """

    class Meta:
        store_results = True
        max_retries = 0

    def perform(self, experiment_id: str, tags: TTags) -> str:
        """
        Creates our simulation task

        Args:
            experiment_id(str): experiment id which the simulation belongs too
            tags(TTags): Tags for the simulation

        Returns:
            (str) The generated simulation uuid
        """
        # we only want to import this here so that clients don't need postgres/sqlalchemy packages
        from idmtools_platform_local.workers.utils import create_or_update_status
        uuid = ''.join(random.choice(string.digits + string.ascii_uppercase) for _ in range(8))

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('Creating simulation %s for experiment %s', uuid, experiment_id)

        # Ensure data directories exist
        data_path = os.path.join(DATA_PATH, experiment_id, uuid)
        os.makedirs(data_path, exist_ok=True)

        # Define our simulation path and our root asset path
        simulation_path = os.path.join(DATA_PATH, experiment_id, uuid)
        asset_dir = os.path.join(DATA_PATH, experiment_id, "Assets")

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('Linking assets from %s to %s', asset_dir, os.path.join(simulation_path, 'Assets'))

        # Link in our asset directory and then add to our system path so any executing programs can see
        # the assets using relative paths.. ie ./Asset/tmp.txt
        os.symlink(asset_dir, os.path.join(simulation_path, 'Assets'))

        # Update
        create_or_update_status(uuid, data_path, tags, parent_uuid=experiment_id)
        return uuid
