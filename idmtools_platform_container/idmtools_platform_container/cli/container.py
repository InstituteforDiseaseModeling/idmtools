"""
idmtools ContainerPlatform CLI commands.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import json
import click
import shutil
import subprocess
from typing import Union
from pathlib import Path
from rich.console import Console
from rich.table import Table
from idmtools.core import ItemType
from idmtools_platform_container.container_operations.docker_operations import list_running_jobs, find_running_job, \
    is_docker_installed, is_docker_daemon_running, get_working_containers, get_containers, get_container
from idmtools_platform_container.utils.job_history import JobHistory
from idmtools_platform_container.utils.status import summarize_status_files, get_simulation_status
from idmtools_platform_container.utils.general import convert_byte_size
from logging import getLogger

logger = getLogger(__name__)
user_logger = getLogger('user')

EXPERIMENT_FILES = ['stdout.txt', 'stderr.txt']
SIMULATION_FILES = ['stdout.txt', 'stderr.txt', 'job_status.txt', 'status.txt', 'output']


##########################
# Container Commands
#########################

@click.group(short_help="Container PLATFORM Related Commands")
def container():
    """
    Commands related to managing the Container Platform.
    """
    pass


@container.command(help="Verify the Docker environment.")
def verify_docker():
    """Check docker environment."""
    if not is_docker_installed():
        user_logger.error("Docker is not installed.")
        exit(-1)

    if not is_docker_daemon_running():
        user_logger.warning("Docker daemon is not running.")
        exit(-1)

    # Check docker version
    result = subprocess.run(['docker', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    console = Console()
    console.print(f"{result.stdout.strip()}.")


@container.command(help="Cancel an Experiment/Simulation job.\n\n"
                        "Arguments:\n\n"
                        "  ITEM_ID: Experiment/Simulation ID or Job ID")
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
    console = Console()
    job = find_running_job(item_id, container_id)
    if job:
        if job.item_type == ItemType.EXPERIMENT:
            kill_cmd = f"docker exec {job.container_id} pkill -TERM -g {job.job_id}"
        else:
            kill_cmd = f"docker exec {job.container_id} kill -9 {job.job_id}"

        result = subprocess.run(kill_cmd, shell=True, stderr=subprocess.PIPE, text=True)  # default: check=False
        if result.returncode == 0:
            console.print(f"Successfully killed {job.item_type.name} {job.job_id}")
        else:
            console.print(f"Error killing {job.item_type.name} {job.item_id}: {result.stderr}")
    else:
        user_logger.warning(f"Not found job {item_id}.")


@container.command(help="Check the status of an Experiment/Simulation.\n\n"
                        "Arguments:\n\n"
                        "  ITEM_ID: Experiment/Simulation ID or Job ID")
@click.argument('item-id', required=True)
@click.option('-c', '--container_id', help="Container Id")
@click.option('-l', '--limit', default=10, help="Max number of simulations to show")
@click.option('--verbose/--no-verbose', default=False, help="Display with working directory or not")
def status(item_id: Union[int, str], container_id: str = None, limit: int = 10, verbose: bool = False):
    """
    Check Experiment/Simulation status.
    Args:
        item_id: Experiment/Simulation ID or Job ID
        container_id: Container ID
        limit: number of simulations to display
        verbose: display simulation details or not
    Returns:
        None
    """
    console = Console()
    item_dir = JobHistory.get_item_path(item_id)
    if item_dir is not None:
        # Experiment/Simulation case
        item_type = item_dir[1]
        if item_type == ItemType.SIMULATION:
            st = get_simulation_status(item_dir[0])
            console.print(f"{item_type.name} {item_id} is {st}.")
        elif item_type == ItemType.EXPERIMENT:
            exp_dir = item_dir[0]
            summarize_status_files(exp_dir, max_display=limit, verbose=verbose)
        else:
            user_logger.warning(f"{item_type.name} {item_id} status id not defined.")
    else:
        # Job ID case
        job = find_running_job(item_id, container_id)
        if job:
            if job.item_type == ItemType.EXPERIMENT:
                job_cache = JobHistory.get_job(job.item_id)
                exp_dir = job_cache['EXPERIMENT_DIR']
                summarize_status_files(exp_dir, max_display=limit, verbose=verbose)
            elif job.item_type == ItemType.SIMULATION:
                console.print(f"Simulation {job.item_id} is RUNNING.")
        else:
            user_logger.warning(f"Job {item_id} not found.")


@container.command(help="List running Experiment/Simulation jobs.\n\n"
                        "Arguments:\n\n"
                        "  CONTAINER_ID: Container ID (optional)")
@click.argument('container-id', required=False)
@click.option('-l', '--limit', default=10, help="Max number of simulations to show")
@click.option('-n', '--next', default=0, type=int, help="Next number of jobs to show")
def jobs(container_id: str = None, limit: int = 10, next: int = 0):
    """
    List running Experiment/Simulation jobs in Container(s).
    Args:
        container_id: Container ID
        limit: number of simulations to display
        next: next number of jobs to show
    Returns:
        None
    """
    containers = get_working_containers(container_id)
    if len(containers) == 0:
        if container_id:
            user_logger.warning(f"Container {container_id} not found.")
        else:
            user_logger.warning("No containers found.")
        return

    for container_id in containers:
        running_jobs = list_running_jobs(container_id)
        if not running_jobs:
            continue

        # Separate jobs by group_pid
        group = {}
        for job in running_jobs:
            if job.group_pid not in group:
                group[job.group_pid] = []
            group[job.group_pid].append(job)

        console = Console()
        for g in group:
            _jobs = group[g]
            # Get total number of running simulations
            total_jobs = len(_jobs)
            # Take the first job which is the experiment
            exp_job = _jobs[0]
            # Skip the first job which is the experiment
            sim_jobs = _jobs[1:]

            start = next * limit
            end = start + limit
            sim_next = sim_jobs[start:end]
            # Include the experiment job
            sim_next.insert(0, exp_job)

            # Skip the first job which is the experiment
            console.print(
                f"[bold][cyan]Experiment[/][/] {exp_job.item_id} on [bold][cyan]Container[/][/] [red]{container_id}[/] has {total_jobs - 1} running [bold][cyan]simulations[/][/].")
            table = Table()
            table.add_column("Entity Type", justify="right", style="cyan", no_wrap=True)
            table.add_column("Entity ID", style="yellow")
            table.add_column("Job ID", justify="right", style="green")
            table.add_column("Container", justify="right", style="plum2")
            table.add_column("Status", justify="right", style="red")

            for job in sim_next:
                table.add_row(job.item_type.name, str(job.item_id), str(job.job_id), job.container_id, 'running')

            console.print(table)


@container.command(help="Retrieve Experiment history.\n\n"
                        "Arguments:\n\n"
                        "  EXP_ID: Experiment ID")
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
        console = Console()
        console.print_json(json.dumps(item, indent=2))


@container.command(help="View the job history.\n\n"
                        "Arguments:\n\n"
                        "  CONTAINER_ID: Container ID")
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

    console = Console()
    console.print(f"There are {len(data)} Experiment cache in history.")
    for job in data_next:
        console.print(f"{'':-^100}")
        for k, v in job.items():
            # Skip some keys
            if k in ('EXPERIMENT_DIR', 'SUITE_ID'):
                continue
            console.print(f"[bold][cyan]{k:16}[/][/]: {v}")


@container.command(help="Locate Suite/Experiment/Simulation file directory.\n\n"
                        "Arguments:\n\n"
                        "  ITEM_ID: Suite/Experiment/Simulation ID")
@click.argument('item-id', type=str, required=True)
def path(item_id: str):
    """
    Find Suite/Experiment/Simulation file directory.
    Args:
        item_id: Suite/Experiment/Simulation ID
    Returns:
        None
    """
    item = JobHistory.get_item_path(item_id)
    if item:
        console = Console()
        console.print(f"{item[1].name}: {item[0]}")


@container.command(help="Check if an Experiment/Simulation is running.\n\n"
                        "Arguments:\n\n"
                        "  ITEM_ID: Experiment/Simulation ID")
@click.argument('item-id', type=str, required=True)
def is_running(item_id: str):
    """
    Check if Experiment/Simulation is running.
    Args:
        item_id: Experiment/Simulation ID
    Returns:
        None
    """
    console = Console()
    job = find_running_job(item_id)
    if job:
        console.print(f"{job.item_type.name} {job.item_id} is running on container {job.container_id}.")
    else:
        # Check if it is a valid Experiment/Simulation ID
        his_path = JobHistory.get_item_path(item_id)
        if his_path:
            # Check item type
            item_type = his_path[1]
            if item_type == ItemType.SUITE:
                console.print(f"{item_id} is not a valid Experiment/Simulation ID.")
            else:
                console.print(f"{item_type.name} {item_id} is not running.")
        else:
            console.print(f"Job {item_id} is not found.")


@container.command(help="Check the history volume.")
def volume():
    """Get job history volume."""
    v = JobHistory.volume()
    mv = convert_byte_size(v)
    console = Console()
    console.print(f"Job history volume: {mv}")


@container.command(help="Clear the job history.\n\n"
                        "Arguments:\n\n"
                        "  CONTAINER_ID: Container ID (optional)")
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


@container.command(help="Sync the file system with job history.")
def sync_history():
    """Sync file system with job history."""
    JobHistory.sync()


@container.command(help="Get the count of count histories.\n\n"
                        "Arguments:\n\n"
                        "  CONTAINER_ID: Container ID (optional)")
@click.argument('container-id', required=False)
def history_count(container_id: str = None):
    """
    Get History Count.
    Args:
        container_id: Container ID
    Returns:
        None
    """
    console = Console()
    console.print(JobHistory.count(container_id))


@container.command(help="Clear job results files and folders.\n\n"
                        "Arguments:\n\n"
                        "  ITEM_ID: Experiment/Simulation ID")
@click.argument('item-id', type=str, required=True)
@click.option('-r', '--remove', multiple=True, help="Extra files/folders to be removed from simulation")
def clear_results(item_id: str, remove: bool = True):
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

    # Get item path
    item = JobHistory.get_item_path(item_id)
    # Check item type
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


@container.command(help="Inspect a container.\n\n"
                        "Arguments:\n\n"
                        "  CONTAINER_ID: Container ID")
@click.argument('container-id', required=True)
def inspect(container_id: str):
    """
    Check container information.
    Args:
        container_id: Container ID
    Returns:
        None
    """
    console = Console()
    container = get_container(container_id)
    if container is None:
        console.print(f"Container {container_id} not found.")
        return

    console.print('-' * 100)
    console.print(f"[bold][cyan]Container ID[/][/]: {container.short_id}")
    console.print(f"[bold][cyan]Container Name[/][/]: {container.name}")
    console.print(f"[bold][cyan]Status[/][/]: {container.status}")
    console.print(f"[bold][cyan]Created[/][/]: {container.attrs['Created']}")
    console.print(f"[bold][cyan]StartedAt[/][/]: {container.attrs['State']['StartedAt']}")

    console.print("[bold][cyan]Image[/][/]:")
    console.print_json(json.dumps(container.attrs['Config']['Image']))

    console.print("[bold][cyan]Image Tags[/][/]:")
    console.print_json(json.dumps(container.image.tags))

    console.print("[bold][cyan]State[/][/]:")
    console.print_json(json.dumps(container.attrs['State']))

    console.print("[bold][cyan]Mounts[/][/]:")
    mounts = [m for m in container.attrs['Mounts'] if m['Type'] == 'bind']
    console.print_json(json.dumps(mounts))


@container.command(help="Stop running container(s).\n\n"
                        "Arguments:\n\n"
                        "  CONTAINER_ID: Container ID (optional)")
@click.argument('container-id', required=False)
@click.option('--remove/--no-remove', default=False, help="Display with working directory or not")
def stop_container(container_id: str = None, remove: bool = False):
    """
    Sopp running container(s).
    Args:
        container_id: container id
        remove: remove container or not
    Returns:
        None
    """
    console = Console()
    # Get working containers
    containers = get_working_containers(container_id, entity=True)
    if len(containers) == 0:
        if container_id:
            user_logger.warning(f"Not found running Container {container_id}.")
        else:
            user_logger.warning("No running containers found.")
        return

    for container in containers:
        container.stop()
        if remove:
            container.remove()
            console.print(f"Container {container.short_id} is stopped and removed.")
        else:
            console.print(f"Container {container.short_id} is stopped.")


@container.command(help="Remove stopped containers.\n\n"
                        "Arguments:\n\n"
                        "  CONTAINER_ID: Container ID (optional)")
@click.argument('container-id', required=False)
def remove_container(container_id: str = None):
    """
    Remove stopped containers.
    Args:
        container_id: container id
    Returns:
        None
    """
    console = Console()
    if container_id:
        container = get_container(container_id)
        if container:
            if container.status != 'running':
                container.remove()
                console.print(f"Container {container_id} is removed.")
            else:
                user_logger.warning(f"Container {container_id} is running, need to stop first.")
        else:
            user_logger.warning(f"Container {container_id} not found.")
        return

    # Remove all stopped containers
    container_list = get_containers(include_stopped=True)['stopped']
    container_removed = []
    for container in container_list:
        container.remove()
        container_removed.append(container.short_id)

    if len(container_removed) > 0:
        console.print(f"{len(container_removed)} container(s) removed.")
    else:
        user_logger.warning("No container removed.")


@container.command(help="pip install a package on a container.\n\n"
                        "Arguments:\n\n"
                        "  PACKAGE: package to be installed")
@click.argument('package', required=True)
@click.option('-c', '--container-id', type=str, help="Container ID")
@click.option('-i', '--index-url', type=str, help="index-url for pip install")
@click.option('-e', '--extra-index-url', type=str, help="extra-index-url for pip install")
def install(package: str, container_id: str, index_url: str = None, extra_index_url: str = None):
    """
    Pip install package on container.
    Args:
        package: package name
        container_id: Container ID
        index_url: index-url for pip install
        extra_index_url: extra-index-url for pip install
    Returns:
        None
    """
    console = Console()
    if index_url:
        package = f"--index-url {index_url} {package}"
    elif extra_index_url:
        package = f"--extra-index-url {extra_index_url} {package}"
    else:
        package = f"{package}"

    command = f'docker exec {container_id} bash -c "pip3 install {package}"'
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        console.print(result.stdout)
    except subprocess.CalledProcessError as e:
        user_logger.error(e.stderr)


@container.command(help="List packages installed on a container.\n\n"
                        "Arguments:\n\n"
                        "  CONTAINER_ID: Container ID")
@click.argument('container-id', required=True)
def packages(container_id: str):
    """
    List packages installed on container.
    Args:
        container_id: Container ID
    Returns:
        None
    """
    console = Console()
    if not JobHistory.verify_container(container_id):
        user_logger.error(f"Container {container_id} not found.")
        return
    command = f'docker exec {container_id} bash -c "pip list"'
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        console.print(result.stdout)
    except subprocess.CalledProcessError as e:
        user_logger.error(e.stderr)


@container.command(help="List running processes in a container.\n\n"
                        "Arguments:\n\n"
                        "  CONTAINER_ID: Container ID")
@click.argument('container-id', required=True)
def ps(container_id: str):
    """
    List running processes in container.
    Args:
        container_id: Container ID
    Returns:
        None
    """
    if not JobHistory.verify_container(container_id):
        user_logger.error(f"Container {container_id} not found.")
        return
    command = f'docker exec {container_id} bash -c "ps -efj"'
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        console = Console()
        console.print(result.stdout)
    except subprocess.CalledProcessError as e:
        user_logger.error(e.stderr)


@container.command(help="List all available containers.")
@click.option('--all/--no-all', default=False, help="Include stopped containers or not")
def list_containers(all: bool = False):
    """
    List available containers.
    Args:
        all: bool, include stopped containers or not
    Returns:
        None
    """
    containers = get_containers(include_stopped=all)

    table = Table()
    table.add_column("Container ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Image", style="bright_magenta")
    table.add_column("Status", style="red")
    table.add_column("Created", style="yellow")
    table.add_column("Name", style="green")

    for status, container_list in containers.items():
        for container in container_list:
            if container.status == 'running':
                status = f"[green]{container.status}[/]"
            else:
                status = f"[red]{container.status}[/]"
            table.add_row(container.short_id, container.attrs['Config']['Image'], status,
                          container.attrs['Created'], container.name)

    console = Console()
    console.print(f"There are {table.row_count} container(s).")
    console.print(table)
