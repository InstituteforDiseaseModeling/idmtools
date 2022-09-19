"""
Here we implement the Metadata operations interface.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List
from idmtools.core import ItemType
from idmtools.core.interfaces.ientity import IEntity


@dataclass
class IMetadataOperations(ABC):
    """
    Operations to handle metadata for SlurmPlatform.
    """
    @abstractmethod
    def get(self, item: IEntity) -> Dict:
        """
        Obtain item's metadata.

        Args:
            item: idmtools entity (Suite, Experiment and Simulation, etc.)
        Returns:
            a key/value dict of metadata from the given item
        """
        pass

    @abstractmethod
    def dump(self, item: IEntity) -> None:
        """
        Save item's metadata to a file.

        Args:
            item: idmtools entity (Suite, Experiment and Simulation, etc.)
        Returns:
            None
        """
        pass

    @abstractmethod
    def load(self, item: IEntity) -> Dict:
        """
        Obtain item's metadata file.

        Args:
            item: idmtools entity (Suite, Experiment and Simulation, etc.)
        Returns:
             key/value dict of item's metadata file
        """
        pass

    @abstractmethod
    def update(self, item: IEntity) -> None:
        """
        Update item's metadata file.

        Args:
            item: idmtools entity (Suite, Experiment and Simulation, etc.)
        Returns:
            None
        """
        pass

    @abstractmethod
    def clear(self, item: IEntity) -> None:
        """
        Clear the item's metadata file.

        Args:
            item: idmtools entity (Suite, Experiment and Simulation, etc.)
        Returns:
            None
        """
        pass

    @abstractmethod
    def filter(self, item_type: ItemType, item_filter: Dict = None) -> List:
        """
        Obtain all items that match the given item_filter key/value pairs passed.

        Args:
            item_type: the type of items to search for matches (simulation, experiment, suite, etc)
            item_filter: a dict of metadata key/value pairs for exact match searching
        Returns:
            a list of matching items
        """
        pass
