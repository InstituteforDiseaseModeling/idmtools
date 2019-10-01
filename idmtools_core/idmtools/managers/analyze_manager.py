import typing

from idmtools.utils.entities import retrieve_experiment

if typing.TYPE_CHECKING:
    from idmtools.core.types import TAnalyzerList


class AnalyzeManager:

    def __init__(self, ids, analyzers: 'TAnalyzerList', platform):
        self.analyzers = analyzers
        self.platform = platform
        self.objects = [platform.get_object(object_id) for object_id in ids]

    def analyze(self):
        pass
