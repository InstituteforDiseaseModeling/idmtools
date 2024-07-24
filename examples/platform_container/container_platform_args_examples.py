# This file contains examples of how to use different arguments of the Platform class for the CONTAINER platform.
import os
from functools import partial
from idmtools.assets import AssetCollection, Asset
from idmtools.builders import SimulationBuilder
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_platform_container.container_operations.docker_operations import stop_container
from idmtools_platform_container.container_platform import ContainerPlatform


def run_platform_with_new_container():
    """
    This function demonstrates how to run a platform with a new_container=True argument which creates a new container
    for the experiment.
    """
    with ContainerPlatform(job_directory="DEST", new_container=True) as platform:
        task = JSONConfiguredPythonTask(script_path=os.path.join("inputs", "python_models", "model.py"),
                                        parameters=(dict(c=0)))
        ts = TemplatedSimulations(base_task=task)
        builder = SimulationBuilder()

        def param_update(simulation, param, value):
            return simulation.task.set_parameter(param, value)

        # now add the sweep to our builder
        builder.add_sweep_definition(partial(param_update, param="a"), range(3))
        ts.add_builder(builder)
        # create experiment from task
        experiment = Experiment.from_template(ts, name="run_platform_with_new_container")
        experiment.run(wait_until_done=True, platform=platform)
        assert experiment.succeeded, f"Experiment {experiment.id} failed."
        assert os.path.exists(f"DEST/{experiment.parent_id}/{experiment.id}"), "experiment directory does not exist."
        # clean up
        stop_container(platform.container_id, remove=True)


def run_platform_with_docker_image():
    """
    This function demonstrates how to run a platform with a docker_image argument which uses a docker image user has
    specified. It can be user's own docker image or a docker image from a registry.
    """
    with ContainerPlatform(job_directory="DEST",
                  docker_image="docker-production.packages.idmod.org/idmtools/container-test:0.0.3") as platform:
        command = "Assets/run.sh"
        task = CommandTask(command=command)
        ac = AssetCollection()
        model_asset = Asset(absolute_path=os.path.join("inputs", "python_models", "run.sh"))
        ac.add_asset(model_asset)
        # create experiment from task
        experiment = Experiment.from_task(task, name="run_platform_with_docker_image", assets=ac)
        experiment.run(wait_until_done=True, platform=platform)
        assert experiment.succeeded, f"Experiment {experiment.id} failed."
        stop_container(platform.container_id, remove=True)


def run_platform_with_force_start():
    """
    This function demonstrates how to run a platform with a force_start=True argument which forces the platform to start
    a new container or stopped container for the experiment.
    """
    with ContainerPlatform(job_directory="DEST", force_start=True) as platform:
        command = "Assets/run.sh"
        task = CommandTask(command=command)
        ac = AssetCollection()
        model_asset = Asset(absolute_path=os.path.join("inputs", "python_models", "run.sh"))
        ac.add_asset(model_asset)
        experiment = Experiment.from_task(task, name="run_platform_with_force_start", assets=ac)
        experiment.run(wait_until_done=True, platform=platform)
        assert experiment.succeeded, f"Experiment {experiment.id} failed."
        stop_container(platform.container_id, remove=True)


def run_platform_with_user_mounts():
    """
    This function demonstrates how to run a platform with a user_mounts argument which mounts user specified directories
    to the container.
    """
    src1 = os.path.join(os.getcwd(), 'inputs', 'python_models')
    src2 = os.path.dirname(os.getcwd())

    user_mounts = {src1: "/home/dest", src2: "/home/dest2"}
    with ContainerPlatform(job_directory="DEST", user_mounts=user_mounts) as platform:
        command = "/home/dest/run.sh"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_platform_with_user_mounts")
        experiment.run(wait_until_done=True, platform=platform)
        assert experiment.succeeded, f"Experiment {experiment.id} failed."
        stop_container(platform.container_id, remove=True)


def run_platform_with_prefix_container_name():
    """
    This function demonstrates how to run a platform with a prefix argument which adds a prefix to the container name.
    Otherwise, the container name is randomly generated.
    """
    with ContainerPlatform(job_directory="DEST", container_prefix="container_prefix") as platform:
        command = "Assets/run.sh"
        task = CommandTask(command=command)
        ac = AssetCollection()
        model_asset = Asset(absolute_path=os.path.join("inputs", "python_models", "run.sh"))
        ac.add_asset(model_asset)
        # create experiment from task
        experiment = Experiment.from_task(task, name="run_platform_with_prefix_container_name", assets=ac)
        experiment.run(wait_until_done=True, platform=platform)
        assert experiment.succeeded, f"Experiment {experiment.id} failed."
        stop_container(platform.container_id, remove=True)


def run_platform_with_custom_data_mount():
    """
    This function demonstrates how to run a platform with a custom data_mount argument which mounts user specified
    directories to the container instead of default dir with /home/container_data.
    """
    with ContainerPlatform(job_directory="DEST", data_mount="/home/data") as platform:
        command = "Assets/run.sh"
        task = CommandTask(command=command)
        ac = AssetCollection()
        model_asset = Asset(absolute_path=os.path.join("inputs", "python_models", "run.sh"))
        ac.add_asset(model_asset)
        # create experiment from task
        experiment = Experiment.from_task(task, name="run_platform_with_custom_data_mount", assets=ac)
        experiment.run(wait_until_done=True, platform=platform)
        assert experiment.succeeded, f"Experiment {experiment.id} failed."
        stop_container(platform.container_id, remove=True)


def run_platform_with_retries():
    """
    This function demonstrates how to run a platform with a retries argument which retries the experiment up to reties #
    if it fails.
    """
    with ContainerPlatform(job_directory="DEST", retries=3) as platform:
        command = "Assets/run.sh"
        task = CommandTask(command=command)
        ac = AssetCollection()
        model_asset = Asset(absolute_path=os.path.join("inputs", "python_models", "run.sh"))
        ac.add_asset(model_asset)
        # create experiment from task
        experiment = Experiment.from_task(task, name="run_platform_with_retries", assets=ac)
        experiment.run(wait_until_done=True, platform=platform)
        assert experiment.succeeded, f"Experiment {experiment.id} failed."
        stop_container(platform.container_id, remove=True)


if __name__ == '__main__':
    run_platform_with_docker_image()
    run_platform_with_new_container()
    run_platform_with_force_start()
    run_platform_with_user_mounts()
    run_platform_with_custom_data_mount()
    run_platform_with_prefix_container_name()
    run_platform_with_retries()
