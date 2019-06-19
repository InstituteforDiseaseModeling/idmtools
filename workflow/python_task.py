from task import Task


class PythonTask(Task):

    def __init__(self, method, method_kwargs, **kwargs):
        self.__init__(**kwargs)
        self.method = method
        self.method_kwargs = method_kwargs

    def run(self):
        super().run()
        self.status = self.RUNNING
        print(f'>>>\nRunning task: {self.name} command: {self.command}')

        try:
            self.method(**self.method_kwargs)
        except Exception as e:
            print(f'Error in task {self.name} type: {type(e)} message: {str(e)}')
            self.status = self.FAILED
        else:
            self.status = self.SUCCESS
        print(f'Task {self.name} result: {self.status}\n<<<')
        return self.status
