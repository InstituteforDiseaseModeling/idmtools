import datetime

import sqlalchemy
from sqlalchemy import Enum, Column, String, DateTime, func, Index
from sqlalchemy.dialects.postgresql import JSON
from idmtools_platform_local.workers.data import Base
from idmtools_platform_local.status import Status


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
    extra_details = Column(JSON, default={})
    created = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, server_default=func.now())
    updated = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self, as_experiment=True):
        result = {k: v for k, v in self.__dict__.items() if k[0] != "_"}
        result['created'] = str(result['created'])
        result['updated'] = str(result['updated'])
        if as_experiment:
            result['experiment_id'] = result['uuid']
            del result['uuid']
            del result['parent_uuid']
        else:
            result['simulation_uid'] = result['uuid']
            del result['uuid']
            result['experiment_id'] = result['parent_uuid']
            del result['parent_uuid']
            result['status'] = str(result['status'])
        return result

    def __str__(self):
        return str(self.to_dict())


# add indexes to accelerate common ops
Index('parent_status_idx', JobStatus.parent_uuid.desc(), JobStatus.status.desc())
Index('created_idx', JobStatus.created.desc())
# add a javascript index
Index(
    'ix_sample',
    sqlalchemy.text("(jsoncol->'values') jsonb_path_ops"),
    postgresql_using="gin")
