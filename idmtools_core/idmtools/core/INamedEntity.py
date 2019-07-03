import typing
from abc import ABCMeta
from dataclasses import dataclass, field

from idmtools.core import IEntity


@dataclass
class INamedEntity(IEntity, metaclass=ABCMeta):
    name: str = field(default=None, metadata={"md": True}, compare=False)

