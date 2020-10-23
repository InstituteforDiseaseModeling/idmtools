import itertools
import logging
from multiprocessing import cpu_count
from dramatiq import GenericActor
from idmtools_platform_local.internals.task_functions.docker_run import docker_perform
from idmtools_platform_local.status import Status

logger = logging.getLogger(__name__)
cpu_sequence = itertools.cycle(range(0, cpu_count() - 1))


try:
    class DockerRunTask(GenericActor):  # pragma: no cover
        class Meta:
            store_results = False
            max_retries = 0
            queue_name = "cpu"

        def perform(self, command: str, experiment_uuid: str, simulation_uuid: str, container_config: dict) -> Status:
            return docker_perform(command, experiment_uuid, simulation_uuid, container_config)

    # it would be great we could just derive from RunTask and change the meta but that doesn't seem to work with
    # GenericActors for some reason. Using BaseTask and these few lines of redundant code are our compromise
    class GPURunTask(GenericActor):  # pragma: no cover
        class Meta:
            store_results = False
            max_retries = 0
            queue_name = "gpu"

        def perform(self, command: str, experiment_uuid: str, simulation_uuid: str, container_config: dict) -> Status:
            return docker_perform(command, experiment_uuid, simulation_uuid, container_config)
except TypeError:  # Doc mocks not working
    pass
