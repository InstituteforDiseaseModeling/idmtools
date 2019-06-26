import os
from abc import ABCMeta
from dataclasses import dataclass
from enum import Enum
import logging

import diskcache

logger = logging.getLogger(__name__)


class IPersistenceService(metaclass=ABCMeta):
    cache_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")
    cache_name = None

    @classmethod
    def _open_cache(cls):
        cache_directory = os.path.join(cls.cache_directory, 'disk_cache', cls.cache_name)
        os.makedirs(cache_directory, exist_ok=True)
        return diskcache.Cache(os.path.join(cls.cache_directory, 'disk_cache', cls.cache_name), timeout=-1)

    @classmethod
    def retrieve(cls, uid):
        cache = cls._open_cache()
        obj = cache.get(uid)
        cache.close()
        return obj

    @classmethod
    def save(cls, obj):
        cache = cls._open_cache()
        if logger.isEnabledFor(logging.DEBUG):
            logging.debug('Saving %s to %s', obj.uid, cls.cache_name)
        cache.set(obj.uid, obj)
        cache.close()
        return obj.uid


class Status(Enum):
    created = 'queued'
    in_progress = 'in_progress'
    failed = 'failed'
    done = 'done'

@dataclass
class JobStatus:
    uid: str
    status: Status = Status.created
    parent_uuid: str = None
    data_path: str = None


class ExperimentDatabase(IPersistenceService):
    cache_name = 'platform'


class SimulationDatabase(IPersistenceService):
    cache_name = 'simulations'