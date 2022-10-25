"""idmtools local platform api config.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import logging
import os
from sqlite3 import OperationalError
import backoff
from flask import Flask
from flask_autoindex import AutoIndex
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from idmtools_platform_local.config import DATA_PATH
from idmtools_platform_local.internals.ui.utils import DateTimeEncoder

static_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static')
application = Flask(__name__, static_url_path="")
if os.getenv('API_LOGGING', '0').lower() in ['1', 't', 'y', 'true', 'yes', 'on', 'debug']:
    application.logger.setLevel(logging.DEBUG)
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', '1') == '1'
application.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI',
                                                          "postgresql+psycopg2://idmtools:idmtools@postgres/idmtools")


db = None


@backoff.on_exception(backoff.constant, OperationalError, max_tries=3, interval=0.2)
def start_db(db=None):
    """Start database for API."""
    if db is None:
        from idmtools_platform_local.internals.data import Base
        from idmtools_platform_local.internals.data.job_status import JobStatus  # noqa: F401
        application.logger.info("Creating DB")
        db = SQLAlchemy(application, session_options=dict(autocommit=True))
        Base.metadata.create_all(db.get_engine(application))
    return db


application.json_encoder = DateTimeEncoder
api = Api(application, prefix='/api')
ai = AutoIndex(application, browse_root=DATA_PATH, add_url_rules=False)
db = SQLAlchemy(application, session_options=dict(autocommit=True))
