from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List

from idmtools.core.interfaces.ientity import IEntity

from idmtools.core import ItemType


class MetadataException(Exception):
    pass


@dataclass
class IMetadataOperations(ABC):

    @abstractmethod
    def get(self, item: IEntity) -> Dict[Any, Any]:
        """
        Obtain all metadata for the given item
        Args:
            item: the item to retrieve metadata for

        Returns: a key/value dict of metadata from the given item
        """
        pass

    @abstractmethod
    def set(self, item: IEntity) -> None:
        """
        Apply the given metadata to the specified item, overwriting any existing metadata key/values.
        Args:
            item: the item to set metadata on

        Returns: Nothing
        """
        pass

    @abstractmethod
    def clear(self, item: IEntity) -> None:
        """
        Delete/empty the metadata for the given item
        Args:
            item: the item to clear metadata from

        Returns: Nothing
        """
        pass

    @abstractmethod
    def filter_items(self, items: List[IEntity], properties: Dict[Any, Any] = None, tags: Dict[Any, Any] = None) \
            -> List[IEntity]:
        """
        Obtain all items that match the given metadata key/value pairs passed. property/tag filters are currently
        expected to be 'equal to' comparisons (key==value) with boolean operator AND between them all.
        Args:
            items: the list of items to search through
            properties: a dict of metadata_key/value pairs for exact match searching (non-tags)
            tags: a dict of metadata_key/value pairs for exact match searching in tags

        Returns: a list of matching items if items
        """

    @abstractmethod
    def filter(self, item_type: ItemType, properties: Dict[Any, Any] = None, tags: Dict[Any, Any] = None) \
            -> List[str]:
        """
        Obtain all item uids of the given type that match the given metadata key/value pairs passed property/tag.
        property/tag filters are currently expected to be 'equal to' comparisons (key==value) with boolean operator AND
        between them all.
        Args:
            item_type: the type of items to search for matches (simulation, experiment, suite, etc)
            properties: a dict of metadata_key/value pairs for exact match searching (non-tags)
            tags: a dict of metadata_key/value pairs for exact match searching in tags

        Returns: a list of item uids
        """
        pass
