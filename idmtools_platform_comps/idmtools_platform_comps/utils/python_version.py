SLURM_ENVIRONMENTS = ['slurmdev', 'slurm2', 'slurmstage', 'calculon']
PYTHON_EXECUTABLE = 'python3'


def platform_task_hooks(task, platform):
    """
    Update task with new python command: python3
    Args:
        task: PythonTask or CommandTask
        platform: the platform user uses

    Returns: re-build task
    """
    try:
        from idmtools_models.python.python_task import PythonTask
        from idmtools.entities.command_task import CommandTask
        if isinstance(task, PythonTask):
            if platform.environment.lower() in SLURM_ENVIRONMENTS and task.python_path.lower() == 'python':
                task.python_path = PYTHON_EXECUTABLE
        elif isinstance(task, CommandTask) and platform.environment.lower() in SLURM_ENVIRONMENTS:
            cmd_list = task.command.executable.split(' ')
            if cmd_list[0].lower() == 'python':
                cmd_list[0] = PYTHON_EXECUTABLE
                task.command.executable = ' '.join(cmd_list)
    except ImportError:
        pass

    return task
