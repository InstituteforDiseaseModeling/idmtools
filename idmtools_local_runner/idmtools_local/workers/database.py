import logging
from typing import List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from idmtools_local.config import SQLALCHEMY_ECHO, SQLALCHEMY_DATABASE_URI

logger = logging.getLogger(__name__)

session_factory: sessionmaker = None


def get_session() -> Session:
    global session_factory
    if session_factory is None:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('Connecting to postgres with URI %s', SQLALCHEMY_DATABASE_URI)
        engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=SQLALCHEMY_ECHO)
        session_factory = sessionmaker(bind=engine)
        from idmtools_local.workers.data.job_status import Base
        logger.info("Creating database schema")
        Base.metadata.create_all(engine)

    return session_factory()


def get_or_create(session: Session, model, filter_args: List[str], **model_args):
    instance = session.query(model).filter_by(**{k:v for k, v in model_args.items() if k in filter_args}).first()
    if instance:
        return instance
    else:
        instance = model(**model_args)
        session.add(instance)
        session.commit()
        return instance