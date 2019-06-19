from task import Task


class PythonTask(Task):

    def __init__(self, method, method_kwargs, **kwargs):
        super().__init__(**kwargs)
        self.method = method
        self.method_kwargs = method_kwargs

    def run(self):
        super().run()
        self.status = self.RUNNING
        print(f'>>>\nRunning task: {self.name}')

        try:
            self.method(**self.method_kwargs)
        except Exception as e:
            print(f'Error in task {self.name} type: {type(e)} message: {str(e)}')
            self.status = self.FAILED
        else:
            self.status = self.SUCCEEDED
        print(f'Task {self.name} result: {self.status}\n<<<')
        return self.status



        """
        When the workflow runner fails, we get tasks stuck in 'running' state. Should not happen!
        Running task: eta command: python --version
        Python 3.7.3
        Task result: succeeded
        <<<
        Not all completed, continuing...
        Got new task for running: theta - unstarted
        >>>
        Running task: theta
        Add result: 3 + 10 = 13
        Traceback (most recent call last):
          File "python-workflow-runner.py", line 40, in <module>
            wf.start()
          File "C:\Users\ckirkman\code\idmtools\workflow\workflow.py", line 32, in start
            task.run()
          File "C:\Users\ckirkman\code\idmtools\workflow\python_task.py", line 22, in run
            self.status = self.SUCCESS
        AttributeError: 'PythonTask' object has no attribute 'SUCCESS'
        (idmtools)
        ckirkman@IDMPPWKS111 MINGW64 ~/code/idmtools/workflow (workflow)
        $ python python-workflow-runner.py
        Initial status of tasks in Workflow:
        {'alpha': 'succeeded',
         'beta': 'succeeded',
         'delta': 'succeeded',
         'epsilon': 'succeeded',
         'eta': 'succeeded',
         'gamma': 'succeeded',
         'theta': 'running',
         'zeta': 'succeeded'}
        Not all completed, continuing...
        No task is ready, waiting...
        Not all completed, continuing...
        No task is ready, waiting...
        Traceback (most recent call last):
          File "python-workflow-runner.py", line 40, in <module>
            wf.start()
          File "C:\Users\ckirkman\code\idmtools\workflow\workflow.py", line 35, in start
            time.sleep(1)
        KeyboardInterrupt
        (idmtools)
        
        
        """