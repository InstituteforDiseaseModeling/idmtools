# Not intended for direct instantiation. Use subclasses
class Task:
    UNSTARTED = 'unstarted'
    RUNNING = 'running'
    FAILED = 'failed'
    SUCCEEDED = 'succeeded'
    READY_STATUSES = [UNSTARTED]
    COMPLETED_STATUSES = [SUCCEEDED, FAILED]

    class NoCacheException(Exception):
        pass

    def __init__(self, name, depends_on=None, executor_args=None, on_error=None):
        self.name = name
        self.depends_on = list() if depends_on is None else depends_on  # These will need to be resolved to dependees
        # TODO: error if we have duplicate dependees
        self.executor_args = dict() if executor_args is None else executor_args
        self.on_error = list() if on_error is None else on_error  # currently unused

        self.dependees = list()
        self.dependents = list()

        self.cache = None

    # TODO: This basic implementation of diskcache-backed state only supports a single Workflow object
    # Duplicate workflows (or ones with in-common task names) will collide.
    @property
    def status(self):
        try:
            s = self.cache[self.name]
        except KeyError:  # it a task is not in the db, add it as unstarted
            s = self.UNSTARTED
            self.status = s
        return s

    @status.setter
    def status(self, value):
        self.cache[self.name] = value
        return self.status

    def set_cache(self, cache):
        self.cache = cache

    def run(self):
        if self.cache is None:
            raise self.NoCacheException('The state cache for the task has not been set. Cannot execute.')
        if self.status not in self.READY_STATUSES:
            raise Exception(f'Cannot run task {self.name}, status: {self.status}. '
                            f'Must be one of: {self.READY_STATUSES}')

    def to_json(self):
        task_dict = {
            'name': self.name,
            'status': self.status,
            'dependees': [task.name for task in self.dependees],
            'dependents': [task.name for task in self.dependents]
        }
        return task_dict
