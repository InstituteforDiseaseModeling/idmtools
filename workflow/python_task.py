from task import Task

import traceback

class PythonTask(Task):

    def __init__(self, method, method_kwargs=None, **kwargs):
        super().__init__(**kwargs)
        self.method = method
        self.method_kwargs = dict() if method_kwargs is None else method_kwargs
        self.kwargs_for_super = kwargs

    def run(self):
        super().run()
        self.status = self.RUNNING
        print(f'>>>\nRunning task: {self.name}')
        try:
            print('%s %s' % (self.method, self.method_kwargs))
            result, next_status = self.method(**self.method_kwargs)
        except:
            print(f'Error in task {self.name}:')
            print(traceback.format_exc())
            next_status = self.FAILED
            # print(f'Error in task {self.name} type: {type(e)} message: {str(e)}')
        else:
            next_status = self.SUCCEEDED if next_status is None else next_status
        self.status = next_status
        print(f'Task {self.name} result: {self.status}\n<<<')
        return self.status
