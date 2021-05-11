"""idmtools local platform simulation actors/queues.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import logging
import typing
from functools import partial
from typing import Dict, Any, List, Tuple
from dramatiq import GenericActor
from idmtools_platform_local.internals.task_functions.simulations import create_simulation

try:
    from sqlalchemy.exc import IntegrityError
except ImportError:  # pragma: no cover
    # we should only hit this on client machines and here it doesn't matter since they never called any methods
    # we use this
    # We mainly want to do this to prevent importing of sqlalchemy on client side installs since it is not needed
    IntegrityError = EnvironmentError


logger = logging.getLogger(__name__)

SIM_ID_LENGTH = 8


class CreateSimulationTask(GenericActor):  # pragma: no cover
    """
    Creates a simulation.

    - Create the simulation folder in the experiment_id parent folder
    - Returns the UUID of the newly created simulation folder
    """

    class Meta:
        """Actor config."""
        store_results = True
        max_retries = 0

    def perform(self, experiment_id: str, tags: Dict[str, Any], extra_details: Dict[str, Any]) -> str:
        """
        Creates our simulation task.

        Args:
            experiment_id(str): experiment id which the simulation belongs too
            tags(TTags): Tags for the simulation
            extra_details: Metadata on the simulation

        Returns:
            (str) The generated simulation uuid
        """
        if extra_details is None:
            extra_details = dict()
        return create_simulation(experiment_id, (tags, extra_details))


class CreateSimulationsTask(GenericActor):  # pragma: no cover
    """
    Creates a simulation.

    - Create the simulation folder in the experiment_id parent folder
    - Returns the UUID of the newly created simulation folder
    """

    class Meta:
        """Actor config."""
        store_results = True
        max_retries = 0

    def perform(self, experiment_id: str, tags: Tuple[List[Dict[str, Any]], Dict[str, Any]]) -> typing.List:
        """
        Creates our simulation task.

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
        create_sim = partial(create_simulation, experiment_id, session=session)
        result = list(map(create_sim, tags))
        session.close()
        return result
