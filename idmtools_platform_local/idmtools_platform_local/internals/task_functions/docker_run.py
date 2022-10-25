"""idmtools local platform docker tasks tools.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
import itertools
import logging
from multiprocessing import cpu_count
from idmtools_platform_local.internals.task_functions.general_task import extract_status, get_current_job, is_canceled
from idmtools_platform_local.internals.workers.utils import get_host_data_bind
from idmtools_platform_local.status import Status

cpu_sequence = itertools.cycle(range(0, cpu_count() - 1))
logger = logging.getLogger(__name__)


def docker_perform(command: str, experiment_uuid: str, simulation_uuid: str, container_config: dict) -> Status:
    """
    Run command in docker.

    Args:
        command: Command to run
        experiment_uuid: Experiment uuid
        simulation_uuid: Simulation uuid
        container_config: Container config.

    Returns:
        Job status
    """
    from idmtools_platform_local.internals.workers.utils import create_or_update_status
    container_config = container_config
    # update the config to container the volume info

    # Define our simulation path and our root asset path
    simulation_path = os.path.join(os.getenv("DATA_PATH", "/data"), experiment_uuid, simulation_uuid)

    container_config['detach'] = True
    container_config['stderr'] = True
    container_config['working_dir'] = simulation_path
    if os.getenv('CURRENT_UID', None) is not None:
        container_config['user'] = os.getenv('CURRENT_UID')
    container_config['auto_remove'] = True
    # we have to mount using the host data path
    data_dir = get_host_data_bind()
    # when using data volumes, we don't usually have to pass this value
    if os.getenv('IDMTOOLS_WORKERS_DATA_MOUNT_BY_VOLUMENAME', None) is None:
        data_dir += "\\" if "\\" in data_dir else "/"
    container_config['volumes'] = {
        data_dir: dict(bind='/data', mode='rw'),
    }
    # limit cpu_workers
    if cpu_count() > 2:
        container_config['cpuset_cpus'] = f'{next(cpu_sequence)}'

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Task Docker Config: {str(container_config)}")

    current_job = get_current_job(experiment_uuid, simulation_uuid, command)
    if is_canceled(current_job):
        return current_job.status

    result = run_container(command, container_config, current_job, simulation_path, simulation_uuid)
    status = extract_status(experiment_uuid, result, simulation_uuid)
    # Update task with the final status
    create_or_update_status(simulation_uuid, status=status, extra_details=current_job.extra_details)
    return status


def run_container(command, container_config, current_job, simulation_path, simulation_uuid):
    """
    Run our docker task.

    Args:
        command: Command to run
        container_config: Docker container config
        current_job: Current job
        simulation_path: Simulation path
        simulation_uuid: Simulation uuid

    Returns:
        Results of job(0 for success, 1 or other code for failures)
    """
    import docker
    from idmtools_platform_local.internals.workers.utils import create_or_update_status

    with open(os.path.join(simulation_path, "StdOut.txt"), "w") as out, \
            open(os.path.join(simulation_path, "StdErr.txt"), "w") as err:  # noqa: F841
        retries = 0
        while retries < 3:
            try:

                client = docker.DockerClient(base_url='unix://var/run/docker.sock')
                dcmd = f'docker run -v {get_host_data_bind()}:/data --user \"{os.getenv("CURRENT_UID")}\" ' \
                    f'-w {container_config["working_dir"]} {container_config["image"]} {command}'
                logger.info(f"Running docker command: {dcmd}")
                logger.info(f"Running {command} with docker config {str(container_config)}")
                out.write(f"{command}\n")

                container = client.containers.run(command=command, **container_config)
                log_reader = container.logs(stream=True)

                current_job.extra_details['container_id'] = container.id
                # Log that we have started this particular simulation
                create_or_update_status(simulation_uuid, status=Status.in_progress, extra_details=current_job.extra_details)
                for output in log_reader:
                    out.write(output.decode("utf-8"))
                result = container.wait()
                return result['StatusCode']
            except Exception as e:
                logger.exception(e)
                err.write(str(e))
                retries += 1
        return -1
