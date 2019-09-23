import typing

if typing.TYPE_CHECKING:
    from idmtools.core import TPlatform
    import uuid


class ExperimentNotFound(Exception):
    def __init__(self, experiment_id: 'uuid', platform: 'TPlatform' = None):
        if platform:
            super().__init__(f"Experiment with id '{experiment_id}' could not be retrieved on platform {platform}.")
        else:
            super().__init__(f"Experiment with id '{experiment_id}' could not be retrieved.")
