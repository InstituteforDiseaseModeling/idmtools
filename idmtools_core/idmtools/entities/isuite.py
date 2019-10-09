import typing
from abc import ABC
from dataclasses import dataclass, field
from idmtools.core.interfaces.iassets_enabled import IAssetsEnabled
from idmtools.core.interfaces.inamed_entity import INamedEntity
from idmtools.entities.icontainer_item import IContainerItem

if typing.TYPE_CHECKING:
    from idmtools.entities.iexperiment import TExperimentList

@dataclass(repr=False)
class ISuite(IContainerItem, INamedEntity, ABC):
    """
    Class that represents a generic suite (a collection of experiments).

    Args:
        experiments: The child items of this suite.
    """
    experiments: 'TExperimentList' = field(default=None, compare=False, metadata={"md": True})
