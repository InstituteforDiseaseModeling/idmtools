"""
PlatformPersistService provides cache for platforms.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from idmtools.services.ipersistance_service import IPersistenceService


class PlatformPersistService(IPersistenceService):
    """
    Provide a cache for our platforms.
    """
    cache_name = "platforms"
