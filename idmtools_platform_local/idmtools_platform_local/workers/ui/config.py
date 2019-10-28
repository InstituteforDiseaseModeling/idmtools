import os

from flask import Flask
from flask_autoindex import AutoIndex
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from idmtools_platform_local.config import DATA_PATH
from idmtools_platform_local.workers.ui.utils import DateTimeEncoder


static_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static')
application = Flask(__name__, static_url_path="")
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS','1') == '1'
application.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI',
                                                          "postgresql+psycopg2://idmtools:idmtools@postgres/idmtools")
application.json_encoder = DateTimeEncoder


db = SQLAlchemy(application)
api = Api(application, prefix='/api')
ai = AutoIndex(application, browse_root=DATA_PATH, add_url_rules=False)

try:
    from idmtools_platform_local.workers.data.job_status import Base
    Base.metadata.create_all(db.get_engine())
except Exception as e:
    pass