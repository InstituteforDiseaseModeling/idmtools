import flask
from datetime import datetime


class DateTimeEncoder(flask.json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return flask.json.JSONEncoder.default(self, o)