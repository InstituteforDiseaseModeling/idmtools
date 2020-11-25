from abc import ABC
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass()
class IWorkOrder(ABC):
    WorkItem_Type: str = field()


@dataclass()
class ExecutionDefinition:
    Command: str = field()
    ImageName: str = field(default='DockerWorker')


@dataclass()
class DockerWorkOrder(IWorkOrder):
    WorkItem_Type: str = field(default='DockerWorker')
    Execution: ExecutionDefinition = field(default_factory=ExecutionDefinition)


@dataclass()
class BuildFlags:
    section: List[str] = field(default_factory=lambda: ['all'])
    library: str = field(default='https://library.sylabs.io')
    Switches: List['str'] = field(default_factory=lambda: [])


@dataclass()
class BuildDefinition:
    Type: str = field(default='singularity')
    Input: str = field(default=None)
    Flags: BuildFlags = field(default_factory=BuildFlags)


@dataclass()
class ImageBuilderWorkOrder(IWorkOrder):
    WorkItem_Type: str = field(default='ImageBuilderWorker')
    Build: str = field(default=BuildDefinition())
    Output: str = field(default='image.sif')
    Tags: Dict[str, str] = field(default_factory=lambda: dict(type='singularity'))
    AdditionalMounts: List[str] = field(default_factory=list)
    StaticEnvironment: Dict[str, str] = field(default_factory=dict)
