import typing
from abc import ABC
from dataclasses import dataclass, field
from idmtools.core.interfaces.IAssetsEnabled import IAssetsEnabled
from idmtools.core.interfaces.INamedEntity import INamedEntity
from idmtools.entities.IContainerItem import IContainerItem

if typing.TYPE_CHECKING:
    from idmtools.core.types import TExperimentsList


@dataclass(repr=False)
class ISuite(IContainerItem, INamedEntity, ABC):
    """
    Represents a generic Suite (of experiments).

    Args:
        experiments: the children items of this suite
    """
    experiments: 'TExperimentsList' = field(default=None, compare=False, metadata={"md": True})
