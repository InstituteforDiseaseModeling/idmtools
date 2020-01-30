import logging
import os
import typing
from functools import partial
from typing import Dict, Any
import backoff as backoff
from dramatiq import GenericActor
import random
import string
try:
    from sqlalchemy.exc import IntegrityError
except ImportError:
    # we should only hit this on client machines and here it doesn't matter since they never called any methods
    # we use this
    # We mainly want to do this to prevent importing of sqlalchemy on client side installs since it is not needed
    IntegrityError = EnvironmentError


logger = logging.getLogger(__name__)

SIM_ID_LENGTH = 8


class CreateSimulationTask(GenericActor):
    """
    Creates a simulation.
    - Create the simulation folder in the experiment_id parent folder
    - Returns the UUID of the newly created simulation folder
    """

    class Meta:
        store_results = True
        max_retries = 0

    @staticmethod
    @backoff.on_exception(backoff.constant, IntegrityError, max_tries=3, interval=0.02, jitter=None)
    def get_uuid_and_data_path(experiment_id, session, tags):
        from idmtools_platform_local.internals.workers.utils import create_or_update_status
        uuid = ''.join(random.choice(string.digits + string.ascii_uppercase) for _ in range(SIM_ID_LENGTH))
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('Creating simulation %s for experiment %s', uuid, experiment_id)
        # create data path
        data_path = os.path.join(os.getenv("DATA_PATH", "/data"), experiment_id, uuid)
        # store info in db to ensure id is unique
        create_or_update_status(uuid, data_path, tags, parent_uuid=experiment_id, session=session,
                                autoclose=session is None)
        return uuid, data_path

    @staticmethod
    def create_simulation(experiment_id: str, tags: Dict[str, Any], session=None):
        # we only want to import this here so that clients don't need postgres/sqlalchemy packages

        uuid, data_path = CreateSimulationTask.get_uuid_and_data_path(experiment_id, session, tags)
        # Ensure data directories exist
        os.makedirs(data_path, exist_ok=True)

        # Define our simulation path and our root asset path
        simulation_path = os.path.join(os.getenv("DATA_PATH", "/data"), experiment_id, uuid)
        asset_dir = os.path.join(os.getenv("DATA_PATH", "/data"), experiment_id, "Assets")

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('Linking assets from %s to %s', asset_dir, os.path.join(simulation_path, 'Assets'))

        # Link in our asset directory and then add to our system path so any executing programs can see
        # the assets using relative paths.. ie ./Asset/tmp.txt
        os.symlink(asset_dir, os.path.join(simulation_path, 'Assets'))

        return uuid

    def perform(self, experiment_id: str, tags: Dict[str, Any]) -> str:
        """
        Creates our simulation task

        Args:
            experiment_id(str): experiment id which the simulation belongs too
            tags(TTags): Tags for the simulation

        Returns:
            (str) The generated simulation uuid
        """
        return CreateSimulationTask.create_simulation(experiment_id, tags)


class CreateSimulationsTask(GenericActor):
    """
    Creates a simulation.
    - Create the simulation folder in the experiment_id parent folder
    - Returns the UUID of the newly created simulation folder
    """

    class Meta:
        store_results = True
        max_retries = 0

    def perform(self, experiment_id: str, tags: typing.List[Dict[str, Any]]) -> typing.List:
        """
        Creates our simulation task

        Args:
            experiment_id(str): experiment id which the simulation belongs too
            tags(TTags): Tags for the simulation

        Returns:
            (str) The generated simulation uuid
        """
        from idmtools_platform_local.internals.workers.utils import get_session
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('Batch Creating simulation for experiment %s', experiment_id)
        session = get_session()
        create_sim = partial(CreateSimulationTask.create_simulation, experiment_id, session=session)
        result = list(map(create_sim, tags))
        session.close()
        return result
