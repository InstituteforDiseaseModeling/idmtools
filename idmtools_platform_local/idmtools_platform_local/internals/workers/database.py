import logging
import os
from multiprocessing import cpu_count
from typing import List
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, Session


from idmtools_platform_local.config import SQLALCHEMY_ECHO

logger = logging.getLogger(__name__)

session_factory: sessionmaker = None
engine = None
default_url = "postgresql+psycopg2://idmtools:idmtools@idmtools_postgres/idmtools"


def get_session() -> Session:
    global session_factory
    print('Connecting to postgres with URI %s', os.getenv('SQLALCHEMY_DATABASE_URI', default_url))
    if session_factory is None:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('Connecting to postgres with URI %s', os.getenv('SQLALCHEMY_DATABASE_URI', default_url))
        engine = get_db()
        session_factory = sessionmaker(bind=engine)
        from idmtools_platform_local.internals.data import Base
        logger.info("Creating database schema")
        retries = 0
        while retries <= 3:
            try:
                Base.metadata.create_all(engine)
                break
            except OperationalError:
                reset_db()
                retries += 1

    return session_factory()


def get_db() -> Engine:
    global engine
    if engine is None:
        engine = create_engine(os.getenv('SQLALCHEMY_DATABASE_URI', default_url), echo=SQLALCHEMY_ECHO,
                               pool_size=cpu_count())
    return engine


def reset_db():
    global engine
    engine = None
    engine = get_db()


def get_or_create(session: Session, model, filter_args: List[str], **model_args):
    instance = session.query(model).filter_by(**{k: v for k, v in model_args.items() if k in filter_args}).first()
    if instance:
        return instance
    else:
        instance = model(**model_args)
        session.add(instance)
        session.commit()
        return instance
