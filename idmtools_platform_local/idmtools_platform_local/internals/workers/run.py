"""idmtools local platform workers entry point.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
# flake8: noqa F821
from logging import getLogger  # pragma: no cover
from idmtools_platform_local.internals.tasks import *
logger = getLogger(__name__)  # pragma: no cover
logger.debug('Starting workers')  # pragma: no cover
