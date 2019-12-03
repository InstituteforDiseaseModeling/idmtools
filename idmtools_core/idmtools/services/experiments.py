from idmtools.services.ipersistance_service import IPersistenceService
import logging

logger = logging.getLogger(__name__)


class ExperimentPersistService(IPersistenceService):
    cache_name = "experiments"

    @classmethod
    def save(cls, obj):
        with cls._open_cache() as cache:
            if logger.isEnabledFor(logging.DEBUG):
                logging.debug('Saving %s to %s', obj.uid, cls.cache_name)
            cache.set(obj.uid, obj.metadata)

        return obj.uid
