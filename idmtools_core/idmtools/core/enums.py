"""
Define our common enums to be used through idmtools.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from pathlib import Path

from enum import Enum

TRUTHY_VALUES = ['1', 'y', 'yes', 'on', 'true', 't', 1, True]
# Used to store idmtools user specific config/data
IDMTOOLS_USER_HOME = Path().home().joinpath(".idmtools")


class EntityStatus(Enum):
    """
    EntityStatus provides status values for Experiment/Simulations/WorkItems.
    """
    COMMISSIONING = 'commissioning'
    CREATED = 'created'
    RUNNING = 'running'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'


class FilterMode(Enum):
    """
    Allows user to specify AND/OR for the filtering system.
    """
    AND = 0
    OR = 1


class ItemType(Enum):
    """
    ItemTypes supported by idmtools.
    """
    SUITE = "Suite"
    EXPERIMENT = "Experiment"
    SIMULATION = "Simulation"
    WORKFLOW_ITEM = "WorkItem"  # On Comps this is workitems
    ASSETCOLLECTION = "Asset Collection"

    def __str__(self):
        """
        Returns a string representation of our item type.

        Returns:
            The string version of our enum value
        """
        return str(self.value)
