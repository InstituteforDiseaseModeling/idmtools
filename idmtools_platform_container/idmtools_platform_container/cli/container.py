"""
idmtools ContainerPlatform CLI commands.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import json
import click
import docker
import shutil
import subprocess
from typing import Union
from pathlib import Path
from tabulate import tabulate
from idmtools.core import ItemType
from idmtools_platform_container.container_operations.docker_operations import list_running_jobs, \
    list_running_containers, get_container, find_running_job
from idmtools_platform_container.utils.job_history import JobHistory
from idmtools_platform_container.utils.status import summarize_status_files, get_simulation_status
from idmtools_platform_container.utils.general import convert_byte_size
from logging import getLogger

logger = getLogger(__name__)
user_logger = getLogger('user')

EXPERIMENT_FILES = ['stdout.txt', 'stderr.txt', 'job_id.txt']
SIMULATION_FILES = ['stdout.txt', 'stderr.txt', 'job_status.txt', 'job_id.txt', 'status.txt', 'output']


##########################
# Container Commands
#########################

@click.group(short_help="Container PLATFORM Related Commands")
def container():
    """
    Commands related to managing the Container Platform.
    """
    pass


def possible_jobid(item_id: str):
    """
    Check if item_id is a job id.
    Args:
        item_id: item id
    Returns:
        bool
    """
    if isinstance(item_id, int) or (isinstance(item_id, str) and item_id.isdigit()):
        return True
    else:
        return False


@container.command(help="Cancel Experiment/Simulation job.")
@click.argument('item-id', required=True)
@click.option('-c', '--container_id', help="Container Id")
def cancel(item_id: Union[int, str], container_id: str = None):
    """
    Cancel Experiment/Simulation job.
    Args:
        item_id: Experiment/Simulation ID or Job ID
        container_id: Container ID
    Returns:
        None
    """
    job = find_running_job(item_id, container_id)
    if job:
        if job.item_type == ItemType.EXPERIMENT:
            kill_cmd = f"docker exec {job.container_id} pkill -TERM -g {job.job_id}"
        else:
            kill_cmd = f"docker exec {job.container_id} kill -9 {job.job_id}"

        result = subprocess.run(kill_cmd, shell=True, stderr=subprocess.PIPE, text=True)  # default: check=False
        if result.returncode == 0:
            user_logger.info(f"Successfully killed {job.item_type.name} {job.job_id}")
        else:
            user_logger.info(f"Error killing {job.item_type.name} {job.item_id}: {result.stderr}")
    else:
        user_logger.warning(f"Not found job {item_id}.")


@container.command(help="Check Experiment/Simulation status.")
@click.argument('item-id', required=True)
@click.option('-c', '--container_id', help="Container Id")
@click.option('-l', '--limit', default=10, help="Max number of simulations to show")
@click.option('--show/--no-show', default=False, help="Display with working directory or not")
def status(item_id: Union[int, str], container_id: str = None, limit: int = 10, show: bool = False):
    """
    Check Experiment/Simulation status.
    Args:
        item_id: Experiment/Simulation ID or Job ID
        container_id: Container ID
        limit: number of simulations to display
        show: display simulation details or not
    Returns:
        None
    """
    if possible_jobid(item_id):
        job = find_running_job(item_id, container_id)
        if job:
            if job.item_type == ItemType.EXPERIMENT:
                job_cache = JobHistory.get_job(job.item_id)
                exp_dir = job_cache['EXPERIMENT_DIR']
                summarize_status_files(exp_dir, max_display=limit, show=show)
            elif job.item_type == ItemType.SIMULATION:
                user_logger.info(f"Simulation {job.item_id} is RUNNING.")
        else:
            user_logger.warning(f"Job {item_id} not found.")
    else:
        item_dir = JobHistory.get_item_path(item_id)
        if item_dir is None:
            user_logger.warning(f"Item {item_id} not found in Job History.")
            exit(-1)

        item_type = item_dir[1]
        if item_type == ItemType.SIMULATION:
            st = get_simulation_status(item_dir[0])
            user_logger.info(f"{item_type.name} {item_id} is {st}.")
        elif item_type == ItemType.EXPERIMENT:
            exp_dir = item_dir[0]
            summarize_status_files(exp_dir, max_display=limit, show=show)
        else:
            user_logger.warning(f"{item_type.name} {item_id} status id not defined.")


@container.command(help="List running Experiment/Simulation jobs")
@click.argument('c', required=False)
def jobs(c: str = None):
    """
    List running Experiment/Simulation jobs in Container(s).
    Args:
        c: Container ID
    Returns:
        None
    """
    if c is None:
        client = docker.from_env()
        containers = [c.short_id for c in client.containers.list()]
    else:
        containers = [c]

    for container_id in containers:
        running_jobs = list_running_jobs(container_id)
        if running_jobs:
            print(tabulate([(job.item_type.name, job.item_id, job.job_id, job.container_id) for job in running_jobs],
                           headers=('Entity Type', "Entity ID", "Job Id", "Container"), tablefmt='psql'))


@container.command(help="Get Suite/Experiment/Simulation file directory.")
@click.argument('exp-id', type=str, required=True)
def get_job(exp_id: str):
    """
    Get Experiment job history.
    Args:
        exp_id: Experiment ID
    Returns:
        None
    """
    item = JobHistory.get_job(exp_id)
    if item:
        user_logger.info(json.dumps(item, indent=2))


@container.command(help="Update Experiment Expire Time.")
@click.argument('exp-id', type=str, required=True)
@click.option('-s', '--second', default=None, type=int, help="New time to expire in seconds")
def update_expire(exp_id: str, second: int = None):
    """
    Get Experiment job history.
    Args:
        exp_id: Experiment ID
        second: New time to expire in seconds
    Returns:
        None
    """
    item = JobHistory.get_job(exp_id)
    if item:
        JobHistory.history.touch(exp_id, expire=second)
        user_logger.info(f"Experiment {exp_id} expire time updated to {second} seconds.")
    else:
        user_logger.warning(f"Experiment {exp_id} not found.")


@container.command(help="View job history.")
@click.argument('container-id', required=False)
@click.option('-l', '--limit', default=10, type=int, help="Max number of jobs to show")
@click.option('-n', '--next', default=0, type=int, help="Next number of jobs to show")
def history(container_id: str = None, limit: int = 10, next: int = 0):
    """
    View job history.
    Args:
        container_id: Container ID
        limit: number of jobs to show
        next: next number of jobs to show
    Returns:
        None
    """
    data = JobHistory.view_history(container_id)

    start = next * limit
    end = start + limit
    data_next = data[start:end]
    for job in data_next:
        # user_logger.info("-" * 100)
        user_logger.info(f"{'':-^100}")
        for k, v in job.items():
            if k in ('EXPERIMENT_DIR', 'SUITE_ID'):
                continue
            user_logger.info(f"{k:16}: {v}")


@container.command(help="Find Suite/Experiment/Simulation file directory.")
@click.argument('item-id', type=str, required=True)
def item_path(item_id: str):
    """
    Find Suite/Experiment/Simulation file directory.
    Args:
        item_id: Suite/Experiment/Simulation ID
    Returns:
        None
    """
    item = JobHistory.get_item_path(item_id)
    if item:
        user_logger.info(f"{item[1].name}: {item[0]}")


@container.command(help="Check if Experiment/Simulation is running.")
@click.argument('item-id', type=str, required=True)
def is_running(item_id: str):
    """
    Check if Experiment/Simulation is running.
    Args:
        item_id: Experiment/Simulation ID
    Returns:
        None
    """
    job = find_running_job(item_id)
    if job:
        user_logger.info(f"{job.item_type.name} {job.item_id} is running on container {job.container_id}.")
    else:
        his = JobHistory.get_item_path(item_id)
        if his:
            item_type = his[1]
            user_logger.info(f"{item_type.name} {item_id} is not running.")
        else:
            user_logger.info(f"Job {item_id} is not found.")


@container.command(help="Cancel experiment/simulation.")
def volume():
    """Get job history volume."""
    v = JobHistory.volume()
    mv = convert_byte_size(v)
    user_logger.info(f"Job history volume: {mv}")


@container.command(help="Cancel experiment/simulation.")
@click.option('--dt', default=None, help="Datetime to expire (format like '2024-06-30 10:25:07 PM')")
def expire(dt: str = None):
    """
    Expire Job History based on input datetime.
    Args:
        dt: datetime to expire
    Returns:
        None
    """
    JobHistory.expire_history(dt=dt)


@container.command(help="Clear Job History.")
@click.argument('container-id', required=False)
def clear_history(container_id: str = None):
    """
    Clear Job History.
    Args:
        container_id: Container ID
    Returns:
        None
    """
    JobHistory.clear(container_id)


@container.command(help="Sync file system with job history.")
def sync_history():
    """Sync file system with job history."""
    JobHistory.sync()


@container.command(help="Get History Count.")
@click.argument('container-id', required=False)
def history_count(container_id: str = None):
    """
    Get History Count.
    Args:
        container_id: Container ID
    Returns:
        None
    """
    user_logger.info(JobHistory.count(container_id))


@container.command(help="Clear generated files/folders")
@click.argument('item-id', type=str, required=True)
@click.option('-r', '--remove', multiple=True, help="list of files/folders to be removed from simulation")
def clear_job(item_id: str, remove: bool = True):
    """
    Clear the generated output files for a job.
    Args:
        item_id: Experiment/Simulation ID
        remove: list of files/folders
    Returns:
        None
    """

    def _clear_simulation(sim_dir, remove_list):
        """
        Delete generated output files for simulation.
        Args:
            sim_dir: simulation directory
            remove_list: extra files to be deleted
        Returns:
            None
        """
        for f in SIMULATION_FILES + list(remove_list):
            if sim_dir.joinpath(f).exists():
                if sim_dir.joinpath(f).is_dir():
                    shutil.rmtree(sim_dir.joinpath(f))
                else:
                    sim_dir.joinpath(f).unlink(missing_ok=True)

    item = JobHistory.get_item_path(item_id)
    item_type = item[1]
    if item_type == ItemType.SIMULATION:
        sim_dir = item[0]
        _clear_simulation(sim_dir, remove)
    elif item_type == ItemType.EXPERIMENT:
        exp_dir = item[0]
        # Delete generated files from experiment past run
        for f in EXPERIMENT_FILES:
            if exp_dir.joinpath(f).exists():
                if exp_dir.joinpath(f).is_dir():
                    shutil.rmtree(exp_dir.joinpath(f))
                else:
                    exp_dir.joinpath(f).unlink(missing_ok=True)

        # Delete generated files for each of simulations
        pattern = '*/metadata.json'
        for meta_file in Path(exp_dir).glob(pattern=pattern):
            sim_dir = meta_file.parent
            _clear_simulation(sim_dir, remove)
    else:
        user_logger.warning("Suite level not supported, must provide Experiment/Simulation ID!")
        exit(-1)


@container.command(help="Check container info.")
@click.argument('container-id', required=False)
def check_container(container_id: str = None):
    """
    Check container information.
    Args:
        container_id: Container ID
    Returns:
        None
    """
    if container_id is not None:
        container = get_container(container_id)
        if container is None:
            user_logger.info(f"Container {container_id} not found.")
            return
        else:
            containers = [container]
    else:
        containers = list_running_containers()

    for container in containers:
        user_logger.info('-' * 100)
        user_logger.info(f"Container ID: {container.short_id}")
        user_logger.info(f"Container Name: {container.name}")
        user_logger.info(f"Image: {container.image.tags}")
        user_logger.info(f"Status: {container.status}")
        user_logger.info(f"Created: {container.attrs['Created']}")
        user_logger.info(f"State: {container.attrs['State']}")
        user_logger.info(f"StartedAt: {container.attrs['State']['StartedAt']}")
        user_logger.info(f"Mounts: {container.attrs['Mounts']}")

        mounts = [m for m in container.attrs['Mounts'] if m['Type'] == 'bind']
        user_logger.info(mounts)
        print()


@container.command(help="Remove stopped containers.")
@click.argument('container-id', required=False)
def clear_container(container_id: str = None):
    """
    Clear stopped containers.
    Args:
        container_id: container id
    Returns:
        None
    """
    if container_id is not None:
        container = get_container(container_id)
        if container is None:
            user_logger.info(f"Container {container_id} not found.")
            return
        else:
            containers = [container]
    else:
        containers = list_running_containers()

    for container in containers:
        if container.status != 'running':
            # container.stop()
            container.remove()


@container.command(help="Get History Containers.")
def container_history():
    """List of job containers."""
    data = JobHistory.container_history()
    user_logger.info(json.dumps(data, indent=2))
