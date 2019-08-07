import typing

if typing.TYPE_CHECKING:
    from idmtools.core import TAsset, TPlatform
    import uuid


# region Assets Exceptions
class DuplicatedAssetError(Exception):
    def __init__(self, asset: 'TAsset'):
        super().__init__(f"{asset} is already present in the collection!")


class ExperimentNotFound(Exception):
    def __init__(self, experiment_id: 'uuid', platform: 'TPlatform' = None):
        if platform:
            super().__init__(f"Experiment with id '{experiment_id}' could not be retrieved on platform {platform}.")
        else:
            super().__init__(f"Experiment with id '{experiment_id}' could not be retrieved.")
