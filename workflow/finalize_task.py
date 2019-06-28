import os

from file_exists_task import FileExistsTask


class FinalizeTask(FileExistsTask):

    def __init__(self, **kwargs):
        path = 'finalized.txt'
        super().__init__(path=path, **kwargs)
