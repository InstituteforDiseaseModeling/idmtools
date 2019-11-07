import logging
import os
import random
import string
from dataclasses import InitVar
import typing as typing

import backoff
from dramatiq import GenericActor
try:
    from sqlalchemy.exc import IntegrityError
except ImportError:
    # we should only hit this on client machines and here it doesn't matter since they never called any methods
    # we use this
    # We mainly want to do this to prevent importing of sqlalchemy on client side installs since it is not needed
    IntegrityError = EnvironmentError

if typing.TYPE_CHECKING:
    from idmtools.core import TTags, TSimulationClass, typing  # noqa: F401

logger = logging.getLogger(__name__)
EXPERIMENT_ID_LENGTH = 8


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

        retries = 0
        while retries <= 3:
            try:
                data_path, uuid = self.get_uuid_and_data_path(simulation_type, tags)
                break
            except IntegrityError:
                retries += 1
        if retries > 3:
            raise ValueError("Could not save experiment id because of conflicting ids")

        asset_path = os.path.join(data_path, "Assets")
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('Creating asset directory for experiment %s at %s', uuid, asset_path)
        os.makedirs(asset_path, exist_ok=True)
        return uuid

    @staticmethod
    @backoff.on_exception(backoff.constant(0.1), IntegrityError, max_tries=3, jitter=None)
    def get_uuid_and_data_path(self, simulation_type, tags):
        # we only want to import this here so that clients don't need postgres/sqlalchemy packages
        from idmtools_platform_local.internals.workers.utils import create_or_update_status
        uuid = ''.join(random.choice(string.digits + string.ascii_uppercase) for _ in range(EXPERIMENT_ID_LENGTH))
        if logger.isEnabledFor(logging.INFO):
            logger.debug('Creating experiment with id %s', uuid)
        # Update the database with experiment
        data_path = os.path.join(os.getenv("DATA_PATH", "/data"), uuid)
        create_or_update_status(uuid, data_path, tags, extra_details=dict(simulation_type=simulation_type))
        return data_path, uuid
