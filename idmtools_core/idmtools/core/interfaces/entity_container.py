"""
EntityContainer definition. EntityContainer provides an envelope for a Parent to container a list of sub-items.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import typing


if typing.TYPE_CHECKING:
    from idmtools.core.interfaces.ientity import IEntity
    from idmtools.core.enums import EntityStatus
    from typing import List


class EntityContainer(list):
    """
    EntityContainer is a wrapper classes used by Experiments and Suites to wrap their children.

    It provides utilities to set status on entities
    """

    def __init__(self, children: 'List[IEntity]' = None):
        """
        Initialize the EntityContainer.

        Args:
            children: Children to initialize with
        """
        super().__init__()
        self.extend(children or [])

    def set_status(self, status: 'EntityStatus'):
        """
        Set status on all the children.

        Args:
            status: Status to set

        Returns:
            None
        """
        for entity in self:
            entity.status = status

    def set_status_for_item(self, item_id, status: 'EntityStatus'):
        """
        Set status for specific sub-item.

        Args:
            item_id: Item id to set status for
            status: Status to set

        Returns:
            None

        Raises:
            ValueError when the item_id is not in the children list
        """
        for entity in self:
            if entity.uid == item_id:
                entity.status = status
                return

        raise ValueError(f"Item with id {item_id} not found in the container")
