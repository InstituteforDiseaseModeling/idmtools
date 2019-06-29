import enum


# This needs to be defined in a location where the cli can access it without needing
# to load any SQL related libraries.

class Status(enum.Enum):
    """
    Our status enum for jobs
    """
    created = 'created'
    in_progress = 'in_progress'
    failed = 'failed'
    done = 'done'

    def __str__(self):
        return str(self.value)
