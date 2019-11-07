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
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', '1') == '1'
application.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI',
                                                          "postgresql+psycopg2://idmtools:idmtools@postgres/idmtools")


@backoff.on_exception(backoff.constant(0.2), OperationalError, max_tries=3)
def start_db():
    from idmtools_platform_local.internals.data import Base
    db = SQLAlchemy(application)
    Base.metadata.create_all(db.get_engine())
    return db


application.json_encoder = DateTimeEncoder
api = Api(application, prefix='/api')
ai = AutoIndex(application, browse_root=DATA_PATH, add_url_rules=False)
db = start_db()
