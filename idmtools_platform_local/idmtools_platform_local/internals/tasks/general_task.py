import itertools
import logging
from multiprocessing import cpu_count
from dramatiq import GenericActor
from idmtools_platform_local.internals.task_functions.general_task import execute_simulation
from idmtools_platform_local.status import Status

logger = logging.getLogger(__name__)
cpu_sequence = itertools.cycle(range(0, cpu_count() - 1))


try:
    class RunTask(GenericActor):  # pragma: no cover
        """
        Run the given `command` in the simulation folder.
        """

        class Meta:
            store_results = False
            max_retries = 0
            queue_name = "cpu"

        def perform(self, command: str, experiment_uuid: str, simulation_uuid: str) -> Status:
            return execute_simulation(command, experiment_uuid, simulation_uuid)
except TypeError:  # we hit this in docs
    pass
