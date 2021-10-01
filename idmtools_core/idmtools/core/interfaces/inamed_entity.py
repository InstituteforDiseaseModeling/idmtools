"""
INamedEntity definition. INamedEntity Provides a class with a name like Experiments or Suites.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from abc import ABCMeta
from dataclasses import dataclass, field

from idmtools.core.interfaces.ientity import IEntity


@dataclass
class INamedEntity(IEntity, metaclass=ABCMeta):
    """
    INamedEntity extends the IEntity adding the name property.
    """
    name: str = field(default=None, metadata={"md": True}, compare=False)
