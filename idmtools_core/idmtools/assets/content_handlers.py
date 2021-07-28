"""
idmtools assets content handlers.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import json


def json_handler(content):
    """
    Dump a json to a string.

    Args:
        content: Content to write

    Returns:
        String on content
    """
    return json.dumps(content)
