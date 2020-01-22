from abc import ABCMeta
from dataclasses import dataclass, field

from idmtools.core.interfaces.ientity import IEntity


@dataclass
class INamedEntity(IEntity, metaclass=ABCMeta):
    name: str = field(default=None, metadata={"md": True}, compare=False)
    platform: 'IPlatform' = field(default=None)
