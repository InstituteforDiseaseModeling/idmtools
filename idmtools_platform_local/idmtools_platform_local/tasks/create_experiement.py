import logging
import os
import random
import string
from dataclasses import InitVar
import typing as typing
from dramatiq import GenericActor
if typing.TYPE_CHECKING:
    from idmtools.core import TTags, TSimulationClass, typing  # noqa: F401

logger = logging.getLogger(__name__)


class CreateExperimentTask(GenericActor):

    class Meta:
        store_results = True
        max_retries = 0

    def perform(self, tags: 'TTags', simulation_type: InitVar['TSimulationClass']) -> str:
        """
        Creates an experiment.
            - Create the folder
            - Also create the Assets folder to hold the experiments assets
            - Return the UUID of the newly created experiment
        Args:
            tags (TTags): Tags for the experiment to be created
            simulation_type(InitVar[TSimulationClass]): Type of simulation we are creating

        Returns:
            (str) Id of created experiment
        """
        # we only want to import this here so that clients don't need postgres/sqlalchemy packages
        from idmtools_platform_local.workers.utils import create_or_update_status
        uuid = ''.join(random.choice(string.digits + string.ascii_uppercase) for _ in range(8))
        if logger.isEnabledFor(logging.INFO):
            logger.debug('Creating experiment with id %s', uuid)

        data_path = os.path.join(os.getenv("DATA_PATH", "/data"), uuid)

        # Update the database with experiment
        create_or_update_status(uuid, data_path, tags, extra_details=dict(simulation_type=simulation_type))

        asset_path = os.path.join(data_path, "Assets")
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('Creating asset directory for experiment %s at %s', uuid, asset_path)
        os.makedirs(asset_path, exist_ok=True)
        return uuid
