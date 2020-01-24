from abc import ABC
from idmtools.core.interfaces.iassets_enabled import IAssetsEnabled
from idmtools.core.interfaces.inamed_entity import INamedEntity


class IWorkItem(IAssetsEnabled, INamedEntity, ABC):
    """
    Interface of work item
    """
    pass
