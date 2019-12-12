from abc import ABC

from idmtools.core.interfaces.iassets_enabled import IAssetsEnabled
from idmtools.core.interfaces.inamed_entity import INamedEntity


class IWorkflowItem(IAssetsEnabled, INamedEntity, ABC):
    pass