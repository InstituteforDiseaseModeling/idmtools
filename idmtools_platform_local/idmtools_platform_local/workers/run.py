# flake8: noqa F821
from logging import getLogger

from idmtools_platform_local.tasks import *
logger = getLogger(__name__)
logger.debug('Starting workers')