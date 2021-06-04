"""
Defines our RelationType enum.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from enum import Enum


class RelationType(Enum):
    """
    An enumeration representing the type of relationship for related entities.
    """
    DependsOn = 0
    Created = 1
