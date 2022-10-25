"""
Defines our TaskProxy object.

The TaskProxy object is mean to reduce the memory requirements of large simulation sets/configurations after provisioning. Instead of keeping the full original object in memory,
the object is replaced with a proxy object with minimal information needed to work with the task.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from typing import Union
from dataclasses import dataclass, field
from idmtools.entities import CommandLine


@dataclass
class TaskProxy:
    """
    This class is used to reduce the memory footprint of tasks after a simulation has been provisioned.
    """
    command: Union[str, CommandLine] = field(default=None)
    is_docker: bool = False
    is_gpu: bool = False

    @staticmethod
    def from_task(task: 'ITask'):  # noqa: F821
        """
        Create a task proxy from a task.

        Args:
            task: Task to proxy

        Returns:
            TaskProxy of task
        """
        from idmtools.core.docker_task import DockerTask
        is_docker = isinstance(task, DockerTask)
        item = TaskProxy(command=task.command, is_docker=is_docker, is_gpu=is_docker and task.use_nvidia_run)
        return item
