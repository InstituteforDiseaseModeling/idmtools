import sys
import typing
from logging import getLogger
from uuid import UUID

if typing.TYPE_CHECKING:
    from idmtools.entities.iplatform import TPlatform

user_logger = getLogger('user')
logger = getLogger(__name__)


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


class DocLink(Exception):
    pass


def idmtools_error_handler(exctype, value: Exception, tb):
    """
    Global exception handler. This will write our errors in a nice format

    Args:
        exctype: Type of exception
        value: Value of the exception
        tb: Traceback

    Returns:
        None
    """
    if hasattr(value, 'doc_link'):
        from idmtools.utils.info import get_help_version_url
        user_logger.error(f"{value.args[0]}. For more details, see {get_help_version_url(value.doc_link)}")

    logger.exception(value)
    # Call native exception manager
    sys.__excepthook__(exctype, value, tb)
