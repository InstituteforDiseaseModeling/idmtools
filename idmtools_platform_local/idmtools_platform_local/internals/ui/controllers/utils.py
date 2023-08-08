"""idmtools local platform api tools.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import six
from flask_restful import abort
from flask_restful.reqparse import Argument
from werkzeug.datastructures import MultiDict


class dotdict(dict):
    """dot.notation access to dictionary attributes."""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


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


class LocalArgument(Argument):
    """Wraps the Argument class from Flask Restful to not error when fetching the json object on non-json requests."""

    def source(self, request):
        """Pulls values off the request in the provided location.

        :param request: The flask request object to parse arguments from
        """
        if isinstance(self.location, six.string_types):
            super().source(request)
        else:
            values = MultiDict()
            for location in self.location:
                if location == "json" and not request.is_json:
                    value = None
                else:
                    value = getattr(request, location, None)
                if callable(value):
                    value = value()
                if value is not None:
                    values.update(value)
            return values

        return MultiDict()
