from dataclasses import dataclass
from enum import Enum
from idmtools.services.IPersistanceService import IPersistenceService


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