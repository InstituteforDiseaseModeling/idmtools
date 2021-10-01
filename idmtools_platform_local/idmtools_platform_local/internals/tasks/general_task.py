"""idmtools local platform task actors/queues.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import itertools
import logging
from contextlib import suppress
from multiprocessing import cpu_count
from dramatiq import GenericActor
from idmtools_platform_local.internals.task_functions.general_task import execute_simulation
from idmtools_platform_local.status import Status

logger = logging.getLogger(__name__)
cpu_sequence = itertools.cycle(range(0, cpu_count() - 1))

with suppress(TypeError):
    class RunTask(GenericActor):  # pragma: no cover
        """
        Run the given `command` in the simulation folder. This is our CPU queue.
        """

        class Meta:
            """Specify some actor config, mainly the queue_name."""
            store_results = False
            max_retries = 0
            queue_name = "cpu"

        def perform(self, command: str, experiment_uuid: str, simulation_uuid: str) -> Status:
            """Execute a task."""
            return execute_simulation(command, experiment_uuid, simulation_uuid)
