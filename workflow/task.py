import subprocess


class Task:
    UNSTARTED = 'unstarted'
    RUNNING = 'running'
    FAILED = 'failed'
    SUCCEEDED = 'succeeded'
    READY_STATUSES = [UNSTARTED]
    COMPLETED_STATUSES = [SUCCEEDED, FAILED]
    SUCCESS_CODE = 0

    def __init__(self, name, command, depends_on=None, executor_args=None, on_error=None, status=None):
        self.name = name
        self.command = command
        self.depends_on = list() if depends_on is None else depends_on  # These will need to be resolved to dependees
        # TODO: error if we have duplicate dependees
        self.executor_args = dict() if executor_args is None else executor_args
        self.on_error = list() if on_error is None else on_error  # currently unused

        self.dependees = list()
        self.dependents = list()

        self.status = self.UNSTARTED if status is None else status

    def run(self):
        if self.status not in self.READY_STATUSES:
            raise Exception(f'Cannot run task {self.name}, status: {self.status}. '
                            f'Must be one of: {self.READY_STATUSES}')
        self.status = self.RUNNING
        print(f'>>>\nRunning task: {self.name} command: {self.command}')
        process_code = subprocess.run(self.command)
        if process_code.returncode == self.SUCCESS_CODE:
            self.status = self.SUCCEEDED
        else:
            self.status = self.FAILED
        print(f'Task result: {self.status}\n<<<')
        return self.status
