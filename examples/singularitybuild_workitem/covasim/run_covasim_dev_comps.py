import io
import os
import shutil
import sys
import zipfile

import requests
from idmtools.assets import AssetCollection
from idmtools.core.platform_factory import Platform
from idmtools.entities import CommandLine
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations


def get_latest_release():
    response = requests.get('https://api.github.com/repos/InstituteforDiseaseModeling/covasim/releases/latest')
    if response.ok:
        content = response.json()
        output_path = os.path.join(os.path.dirname(__file__), '.covasim_versions', content["tag_name"])
        if not os.path.exists(output_path):
            df_name = f'{output_path}.download'
            response = requests.get(content['zipball_url'], stream=True)
            with zipfile.ZipFile(io.BytesIO(response.content), 'r') as zf:
                zf.extractall(df_name)

            shutil.move(os.path.join(df_name, os.listdir(df_name)[0]), output_path)
            os.rmdir(df_name)
        return output_path
    else:
        raise ValueError(f"Could not find the latest release. {response.status_code}: {response.text}")


if __name__ == "__main__":
    here = os.path.dirname(__file__)

    # Create a platform to run the workitem
    platform = Platform("CALCULON")

    # get from github
    release_path = get_latest_release()

    # create commandline input for the task
    command = CommandLine("singularity exec ./Assets/covasim_ubuntu.sif python3 Assets/run_sim.py")
    task = CommandTask(command=command)
    task.common_assets.add_directory(os.path.join(release_path, 'covasim'), relative_path='covasim')
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
