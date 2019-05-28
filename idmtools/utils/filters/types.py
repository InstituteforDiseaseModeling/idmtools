from enum import Enum
from typing import List, Callable

from assets.Asset import Asset

AssetFilterList = List[Callable[[Asset], bool]]

class FilterMode(Enum):
    AND = 0
    OR = 1