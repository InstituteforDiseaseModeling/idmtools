from typing import Union
from dataclasses import dataclass, field
from idmtools.entities import CommandLine


@dataclass
class TaskProxy:
    """
    This class is used to reduce the memory footprint of tasks after a simulation has been provisioned
    """
    command: Union[str, CommandLine] = field(default=None)
    is_docker: bool = False
    is_gpu: bool = False

    @staticmethod
    def from_task(task: 'ITask'):  # noqa: F821
        from idmtools.core.docker_task import DockerTask
        is_docker = isinstance(task, DockerTask)
        item = TaskProxy(command=task.command, is_docker=is_docker, is_gpu=is_docker and task.use_nvidia_run)
        return item
