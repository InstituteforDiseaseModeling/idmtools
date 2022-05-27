from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List
from idmtools.core.interfaces.ientity import IEntity
from idmtools.core import ItemType


@dataclass
class IMetadataOperations(ABC):

    @abstractmethod
    def get(self, item: IEntity) -> Dict[Any, Any]:
        """
        Obtain item's metadata.
        Args:
            item: the item to retrieve metadata for
        Returns:
            a key/value dict of metadata from the given item
        """
        pass

    @abstractmethod
    def dump(self, item: IEntity) -> None:
        """
        Save item's metadata to a file.
        Args:
            item: the item to get metadata saved
        Returns:
            None
        """
        pass

    @abstractmethod
    def load(self, item: IEntity) -> Dict[Any, Any]:
        """
        Obtain item's metadata file.
        Args:
            item: the item to retrieve metadata from
        Returns:
             key/value dict of metadata from the given item
        """
        pass

    @abstractmethod
    def set(self, item: IEntity) -> None:
        """
        Update item's metadata file.
        Args:
            item: update the item's metadata file
        Returns:
            None
        """
        pass

    @abstractmethod
    def clear(self, item: IEntity) -> None:
        """
        Clear the item's metadata file.
        Args:
            item: clear the item's metadata file
        Returns:
            None
        """
        pass

    @abstractmethod
    def filter(self, item_type: ItemType, properties: Dict[Any, Any] = None) -> List[IEntity]:
        """
        Obtain all items that match the given properties key/value pairs passed.
        Args:
            item_type: the type of items to search for matches (simulation, experiment, suite, etc)
            properties: a dict of metadata key/value pairs for exact match searching
        Returns:
            a list of matching items
        """
        pass
