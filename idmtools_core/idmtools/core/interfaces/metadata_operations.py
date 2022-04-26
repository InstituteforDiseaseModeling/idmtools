from abc import ABC, abstractmethod
from typing import List, Dict

from idmtools.core import ItemType
from idmtools.core.interfaces.iitem import IItem


class MetadataException(Exception):
    pass


class MetadataOperations(ABC):

    @abstractmethod
    def get(self, item: IItem) -> Dict[str, str]:
        """
        Obtain all metadata for the given item
        Args:
            item: the item to retrieve metadata from

        Returns: a key/value dict of metadata from the given item
        """
        pass

    @abstractmethod
    def update(self, item: IItem, metadata: Dict[str, str]) -> Dict[str, str]:
        """
        Apply the given metadata to the specified item, overwriting any existing, matching metadata key/values.
        This is effectively a union between the old and new metadata, with conflicts resolved in favor of the new
        metadata.
        Args:
            item: the item to update metadata on
            metadata: the metadata key/value pairs to add/modify on the item

        Returns: a key/value dict of fully-updated metadata from the given item
        """
        pass

    @abstractmethod
    def clear(self, item: IItem) -> None:
        """
        Delete/empty the metadata for the given item
        Args:
            item: the item to clear metadata from

        Returns: True/False for success/failure
        """
        pass

    @abstractmethod
    def filter(self, filter: Dict[str, str], item_type=ItemType.SIMULATION) -> List[IItem]:
        """
        Obtain all items that match the given metadata key/value pairs passed
        Args:
            filter: a dict of metadata_key/value pairs for exact match searching
            item_type: the type of items to search for matches (simulation, experiment, suite, etc)

        Returns: a list of matching items
        """
        pass
