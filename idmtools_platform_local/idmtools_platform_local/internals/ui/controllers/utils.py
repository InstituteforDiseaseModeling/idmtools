"""idmtools local platform api tools.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from flask_restful import abort


def validate_tags(tags):
    """
    Ensure tags are valid.

    Args:
        tags: Tags to validate

    Returns:
        None
    """
    # validate the tags
    if tags is not None:
        for i in range(len(tags)):
            if ',' in tags[i]:
                tags[i] = tags[i].split(',')

            if type(tags[i]) not in [list, tuple] or len(tags[i]) > 2:
                abort(400, message='Tags needs to be in the format "name,value"')
