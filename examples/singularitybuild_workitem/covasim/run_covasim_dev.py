import io
import os
import shutil
import sys
import zipfile
from logging import getLogger
from pathlib import PurePath
import requests
from idmtools.assets import AssetCollection
from idmtools.core.platform_factory import Platform
from idmtools.entities import CommandLine
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations

logger = getLogger('user')


def get_latest_release(version: str = None) -> PurePath:
    response = requests.get('https://api.github.com/repos/InstituteforDiseaseModeling/covasim/tags')
    if response.ok:
        tags = response.json()
        if version:
            tag = [x for x in tags if x["name"] == version]
            if len(tag) == 0:
                raise ValueError(f"Could not find the tag {version}")
            tag = tag.pop()
        else:
            tag = tags.pop()
        output_path = PurePath(__file__).parent.joinpath('.covasim_versions', tag["name"])
        if not os.path.exists(output_path):
            df_name = f'{output_path}.download'
            response = requests.get(tag['zipball_url'], stream=True)
            logger.info(f'Downloading covasim version: {tag["name"]}')
            with zipfile.ZipFile(io.BytesIO(response.content), 'r') as zf:
                zf.extractall(df_name)

            shutil.move(PurePath(df_name).joinpath(os.listdir(df_name)[0]), output_path)
            logger.debug('Removing temp download directory')
            os.rmdir(df_name)
        return output_path
    else:
        raise ValueError(f"Could not find the latest release. {response.status_code}: {response.text}")


if __name__ == "__main__":
    here = os.path.dirname(__file__)

    # Create a platform to run the work-item
    platform = Platform("CALCULON")

    # get from github
    release_path = get_latest_release()

    # create commandline input for the task
    command = CommandLine("singularity exec ./Assets/covasim_ubuntu.sif python3 Assets/run_sim.py")
    task = CommandTask(command=command)

    # If you wanted to load from a local repo, you could just provide that
    # path instead of the github and disable the download on line 53
    task.common_assets.add_directory(release_path.joinpath('covasim'), relative_path='covasim')
    ts = TemplatedSimulations(base_task=task)
    # Add our image
    task.common_assets.add_assets(AssetCollection.from_id_file("covasim.id"))

    experiment = Experiment.from_task(
        task,
        name=os.path.split(sys.argv[0])[1],
        tags=dict(type='singularity', description='run covasim')
    )
    experiment.add_asset(os.path.join("inputs", "run_sim.py"))
    experiment.run(wait_until_done=True)
    # If we succeed, mark the experiment with an id file
    if experiment.succeeded:
        experiment.to_id_file("dev.id")
