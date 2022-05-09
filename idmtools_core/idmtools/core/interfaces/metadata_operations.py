from abc import ABC, abstractmethod
from typing import Any, Dict, List

from idmtools.core.interfaces.ientity import IEntity

from idmtools.core import ItemType


class MetadataException(Exception):
    pass


class MetadataOperations(ABC):

    @abstractmethod
    def get(self, item: IEntity, item_type: ItemType = ItemType.SIMULATION) -> Dict[Any, Any]:
        """
        Obtain all metadata for the given item
        Args:
            item: the item to retrieve metadata from
            item_type: the type of item that "item" is

        Returns: a key/value dict of metadata from the given item
        """
        pass

    @abstractmethod
    def set(self, item: IEntity, metadata: Dict[Any, Any], item_type: ItemType = ItemType.SIMULATION) -> Dict[Any, Any]:
        """
        Apply the given metadata to the specified item, overwriting any existing metadata key/values.
        Args:
            item: the item to set metadata on
            metadata: the metadata key/value pairs to set on the item
            item_type: the type of item that "item" is

        Returns: a key/value dict of fully-updated metadata from the given item
        """
        pass

    @abstractmethod
    def update(self, item: IEntity, metadata: Dict[Any, Any], item_type: ItemType = ItemType.SIMULATION) \
            -> Dict[Any, Any]:
        """
        Apply the given metadata to the specified item, overwriting any existing, matching metadata key/values.
        This is effectively a union between the old and new metadata, with conflicts resolved in favor of the new
        metadata.
        Args:
            item: the item to update metadata on
            metadata: the metadata key/value pairs to add/modify on the item
            item_type: the type of item that "item" is

        Returns: True/False for success/failure
        """
        pass

    @abstractmethod
    def clear(self, item: IEntity, item_type: ItemType = ItemType.SIMULATION) -> None:
        """
        Delete/empty the metadata for the given item
        Args:
            item: the item to clear metadata from
            item_type: the type of item that "item" is

        Returns: True/False for success/failure
        """
        pass

    @abstractmethod
    def filter(self, filter: Dict[Any, Any], item_type: ItemType = ItemType.SIMULATION) -> List[IEntity]:
        """
        Obtain all items that match the given metadata key/value pairs passed
        Args:
            filter: a dict of metadata_key/value pairs for exact match searching
            item_type: the type of items to search for matches (simulation, experiment, suite, etc)

        Returns: a list of matching items
        """
        pass
