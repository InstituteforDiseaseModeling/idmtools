import logging
import os
from dramatiq import GenericActor
from idmtools_local.config import DATA_PATH
from idmtools_local.data import save_simulation_status

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

    def perform(self, experiment_id):
        import random
        import string
        uuid = ''.join(random.choice(string.digits + string.ascii_uppercase) for _ in range(5))

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('Creating simulation %s for experiment %s', uuid, experiment_id)

        os.makedirs(os.path.join(DATA_PATH, experiment_id, uuid), exist_ok=True)
        save_simulation_status(uuid, experiment_id)
        return uuid