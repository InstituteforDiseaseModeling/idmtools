from enum import Enum
from typing import List, Callable

from idmtools.assets import Asset

# Type for a list of filters to filter assets
# Used in the AssetCollection
AssetFilter = Callable[[Asset], bool]
AssetFilterList = List[AssetFilter]


class FilterMode(Enum):
    """
    Allow to specify AND/OR for the filtering system
    """
    AND = 0
    OR = 1