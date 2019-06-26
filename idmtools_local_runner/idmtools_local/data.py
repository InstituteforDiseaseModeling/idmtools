import os
from abc import ABCMeta
from typing import List

import backoff

from idmtools_local.config import DATA_PATH
from dataclasses import dataclass
from enum import Enum
import logging
import diskcache


logger = logging.getLogger(__name__)


class IPersistenceService(metaclass=ABCMeta):
    cache_directory = os.path.join(DATA_PATH, "db")
    cache_name = None

    @classmethod
    def _open_cache(cls):
        cache_directory = os.path.join(cls.cache_directory, cls.cache_name)
        os.makedirs(cache_directory, exist_ok=True)
        return diskcache.Cache(os.path.join(cls.cache_directory, cls.cache_name), timeout=-1)

    @classmethod
    def retrieve(cls, uid):
        cache = cls._open_cache()
        obj = cache.get(uid, None)
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

    def __str__(self):
        return str(self.value)

@dataclass
class JobStatus:
    uid: str
    status: Status = Status.created
    parent_uuid: str = None
    data_path: str = None
    tags: List[str] = None


class ExperimentDatabase(IPersistenceService):
    cache_name = 'platform'


class SimulationDatabase(IPersistenceService):
    cache_name = 'simulations'


@backoff.on_exception(backoff.expo, diskcache.core.Timeout)
def save_simulation_status(uuid, experiment_id, tags, status=Status.created):
    if tags is None:
        tags = []

    simulation_status = SimulationDatabase.retrieve(uuid)
    if simulation_status is None:
        simulation_status: JobStatus = JobStatus(uid=uuid, parent_uuid=experiment_id,
                                                 data_path=os.path.join(DATA_PATH, experiment_id, uuid),
                                                 tags=tags,
                                                 status=status)
    else:
        simulation_status.status = status
    SimulationDatabase.save(simulation_status)