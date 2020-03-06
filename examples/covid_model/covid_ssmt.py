import os
from dataclasses import dataclass, InitVar

from idmtools.assets import Asset
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem


@dataclass
class COVID19SSMT(SSMTWorkItem):
    covid_abm_path: InitVar[str] = None
    run_script: InitVar[str] = None

    def __post_init__(self, covid_abm_path, run_script):
        super().__post_init__()
        # Change the docker image to have all dependencies installed for covid_abm
        self.docker_image = "ubuntu18.04_python3.6_covid-abm"

        # Add the model to the pyPackages
        self.asset_files.add_path(covid_abm_path, relative_path="pyPackages", recursive=True)

        # Create and add the run file
        run_file_content = f"export PYTHONPATH=./Assets/pyPackages\npython3 {os.path.basename(run_script)}"
        self.user_files.add_asset_file(Asset(filename="run.sh", content=run_file_content))

        # Add the user script
        run_script = os.path.abspath(run_script)
        self.user_files.add_file(run_script)

        # Set the command
        self.command = "./run.sh"
