SLURM_ENVIRONMENTS = ['slurmdev', 'slurm2', 'slurmstage']
PYTHON_EXECUTABLE = 'python3'


def platform_task_hooks(task, platform):
    try:
        from idmtools_models.python.python_task import PythonTask
        if isinstance(task, PythonTask):
            # check if we are on slurm and python_path has not been changed
            if platform.environment.lower() in SLURM_ENVIRONMENTS and task.python_path == 'python':
                task.python_path = PYTHON_EXECUTABLE
    except ImportError:
        pass

    return task


def platform_command_hooks(command, platform):
    try:
        from idmtools.entities import CommandLine
        if isinstance(command, CommandLine):
            # check if we are on slurm and python_path has not been changed
            if platform.environment.lower() in SLURM_ENVIRONMENTS and command.executable.lower() == 'python':
                command.executable = PYTHON_EXECUTABLE
    except ImportError:
        pass

    return command
