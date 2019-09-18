import typing
from abc import ABC
from dataclasses import dataclass, field
from idmtools.core.interfaces.IAssetsEnabled import IAssetsEnabled
from idmtools.core.interfaces.INamedEntity import INamedEntity
from idmtools.entities.icontainer_item import IContainerItem

if typing.TYPE_CHECKING:
    from idmtools.entities.iexperiment import TExperimentList

@dataclass(repr=False)
class ISuite(IContainerItem, INamedEntity, ABC):
    """
    Represents a generic Suite (of experiments).

    Args:
        experiments: the children items of this suite
    """
    experiments: 'TExperimentList' = field(default=None, compare=False, metadata={"md": True})
