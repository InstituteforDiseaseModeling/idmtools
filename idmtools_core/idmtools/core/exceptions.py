import typing
from uuid import UUID

if typing.TYPE_CHECKING:
    from idmtools.entities.iplatform import TPlatform


class ExperimentNotFound(Exception):
    def __init__(self, experiment_id: UUID, platform: 'TPlatform' = None):
        if platform:
            super().__init__(f"Experiment with id '{experiment_id}' could not be retrieved on platform {platform}.")
        else:
            super().__init__(f"Experiment with id '{experiment_id}' could not be retrieved.")


class UnknownItemException(Exception):
    def __init__(self, err: 'str'):
        super().__init__(err)


class NoPlatformException(Exception):
    """
    Cannot find a platform matching the one requested by user
    """
    pass


class TopLevelItem(Exception):
    """
    Thrown when a parent of a top-level item is requested by the platform
    """
    pass


class UnsupportedPlatformType(Exception):
    """
    Occurs when an item is not supported by a platform but is requested
    """
    pass


class NoTaskFound(Exception):
    pass
