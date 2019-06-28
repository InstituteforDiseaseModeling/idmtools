
import enum
from sqlalchemy import  Enum, Column, String
from sqlalchemy.dialects.postgresql import JSON
from idmtools_local.data import Base


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


class JobStatus(Base):
    """
    Generic status table. At moment we only have one which contains both experiments and simulations
    We do it this way to allow for more flexible support in future for non-dtk-ish workflows(ie a bunch of single jobs
    instead of an experiment with sub simulations
    """
    __tablename__ = 'job_status'
    uuid = Column(String(), unique=True, nullable=False, primary_key=True)
    parent_uuid = Column(String(), nullable=True)
    status = Column(Enum(Status), nullable=False, default=Status.created)
    data_path = Column(String(), nullable=False)
    tags = Column(JSON, default=[])



