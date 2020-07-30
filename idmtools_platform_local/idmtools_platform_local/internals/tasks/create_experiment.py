import logging
import os
import random
import string
from typing import Dict, Any

import backoff
from dramatiq import GenericActor
try:
    from sqlalchemy.exc import IntegrityError
except ImportError:
    # we should only hit this on client machines and here it doesn't matter since they never called any methods
    # we use this
    # We mainly want to do this to prevent importing of sqlalchemy on client side installs since it is not needed
    IntegrityError = EnvironmentError


logger = logging.getLogger(__name__)
EXPERIMENT_ID_LENGTH = 8


class CreateExperimentTask(GenericActor):

    class Meta:
        store_results = True
        max_retries = 0

    def perform(self, tags: Dict[str, Any], extra_details: Dict[str, Any] = None) -> str:
        """
        Creates an experiment.
            - Create the folder
            - Also create the Assets folder to hold the experiments assets
            - Return the UUID of the newly created experiment

        Args:
            tags (TTags): Tags for the experiment to be created

        Returns:
            (str) Id of created experiment
        """

        retries = 0
        data_path = None
        uuid = None
        if extra_details is None:
            extra_details = dict()
        while retries <= 3:
            try:
                data_path, uuid = self.get_uuid_and_data_path(tags, extra_details)
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
    @backoff.on_exception(backoff.constant, IntegrityError, max_tries=3, interval=0.02, jitter=None)
    def get_uuid_and_data_path(tags, extra_details):
        # we only want to import this here so that clients don't need postgres/sqlalchemy packages
        from idmtools_platform_local.internals.workers.utils import create_or_update_status
        uuid = ''.join(random.choice(string.digits + string.ascii_uppercase) for _ in range(EXPERIMENT_ID_LENGTH))
        if logger.isEnabledFor(logging.INFO):
            logger.debug('Creating experiment with id %s', uuid)
        # Update the database with experiment
        data_path = os.path.join(os.getenv("DATA_PATH", "/data"), uuid)
        create_or_update_status(uuid, data_path, tags, extra_details=extra_details)
        return data_path, uuid
