"""idmtools local platform api utils.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import json
from datetime import datetime


class DateTimeEncoder(json.JSONEncoder):
    """Json encoder to handle datetimes."""
    def default(self, o):
        """Encode data times use isoformat."""
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)
