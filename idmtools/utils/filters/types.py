from enum import Enum
from typing import List, Callable

from assets.Asset import Asset

# Type for a list of filters to filter assets
# Used in the AssetCollection
AssetFilterList = List[Callable[[Asset], bool]]


class FilterMode(Enum):
    """
    Allow to specify AND/OR for the filtering system
    """
    AND = 0
    OR = 1