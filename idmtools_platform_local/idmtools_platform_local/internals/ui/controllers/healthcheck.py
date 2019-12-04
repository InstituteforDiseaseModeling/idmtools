from flask_restful import Resource
from idmtools_platform_local import __version__
from idmtools_platform_local.internals.ui.config import db

exists_query = "SELECT EXISTS ( SELECT 1 FROM pg_tables WHERE tablename = 'job_status')"


class HealthCheck(Resource):
    def get(self):
        result = db.engine.execute(exists_query).first()
        return dict(
            db=result[0],
            version=__version__
        )
