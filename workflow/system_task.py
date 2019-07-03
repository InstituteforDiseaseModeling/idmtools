import subprocess
from task import Task


class SystemTask(Task):

    SUCCESS_CODE = 0

    def __init__(self, command, **kwargs):
        super().__init__(**kwargs)
        self.command = command

    def run(self):
        super().run()
        self.status = self.RUNNING
        print(f'>>>\nRunning task: {self.name} command: {self.command}')
        process_code = subprocess.run(self.command)
        if process_code.returncode == self.SUCCESS_CODE:
            self.status = self.SUCCEEDED
        else:
            self.status = self.FAILED
        print(f'Task result: {self.status}\n<<<')
        return self.status
