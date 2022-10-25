"""idmtools local platform healthcheck controller(API).

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from flask_restful import Resource
from idmtools_platform_local import __version__
from idmtools_platform_local.internals.ui.config import db

exists_query = "SELECT EXISTS ( SELECT 1 FROM pg_tables WHERE tablename = 'job_status')"


class HealthCheck(Resource):
    """Provide Healthcheck API."""
    def get(self):
        """Get healthcheck."""
        result = db.engine.execute(exists_query).first()
        return dict(
            db=result[0],
            version=__version__
        )
