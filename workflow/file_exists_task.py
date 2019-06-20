import os

from python_task import PythonTask


class FileExistsTask(PythonTask):

    def __init__(self, path, **kwargs):
        kwargs['method'] = FileExistsTask.fail_if_file_does_not_exist
        kwargs['method_kwargs'] = {'path': path}
        super().__init__(**kwargs)

    @staticmethod
    def fail_if_file_does_not_exist(path):
        if not os.path.exists(path):
            raise Exception(f'Expected file does not exist: {path}')

