"""idmtools local platform statuses.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import enum


# This needs to be defined in a location where the cli can access it without needing
# to load any SQL related libraries.

class Status(enum.Enum):
    """
    Our status enum for jobs.
    """
    created = 'created'
    in_progress = 'in_progress'
    canceled = 'canceled'
    failed = 'failed'
    done = 'done'

    def __str__(self):
        """Represent as string using the value."""
        return str(self.value)
