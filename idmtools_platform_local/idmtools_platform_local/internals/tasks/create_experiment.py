"""idmtools local platform experiment actors/queues.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from typing import Dict, Any
from dramatiq import GenericActor
from idmtools_platform_local.internals.task_functions.experiments import create_experiment

try:
    from sqlalchemy.exc import IntegrityError
except ImportError:  # pragma: no cover
    # we should only hit this on client machines and here it doesn't matter since they never called any methods
    # we use this
    # We mainly want to do this to prevent importing of sqlalchemy on client side installs since it is not needed
    IntegrityError = EnvironmentError


class CreateExperimentTask(GenericActor):  # pragma: no cover
    """Experiment actor. Create our experiments, asset collections, and directories."""
    class Meta:
        """Actor config."""
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
        return create_experiment(tags, extra_details)
