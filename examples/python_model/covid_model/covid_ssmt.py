import os
from dataclasses import dataclass, InitVar

from idmtools.assets import Asset
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem


@dataclass
class COVID19SSMT(SSMTWorkItem):
    """
    Class to enable running the covid_abm model on SSMT.
    We are inheriting from SSMTWorkItem to run the covid_abm simulations in a SSMT Work Item and adding a few features:
    - Allowing the user to give the covid_abm model path to automatically upload it along with the simulations
    - Allowing the user to provide a script to run on the worker

    We also automatically set the correct docker image containing all the dependencies for the covid_abm model.
    """
    covid_abm_path: InitVar[str] = None
    run_script: InitVar[str] = None

    def __post_init__(self, covid_abm_path, run_script):
        super().__post_init__()
        # Change the docker image to have all dependencies installed for covid_abm
        self.docker_image = "ubuntu18.04_python3.6_covid-abm"

        # Add the model to the pyPackages
        self.asset_files.add_path(covid_abm_path, relative_path="pyPackages/covid_abm", recursive=True)

        # Create and add the run file
        run_file_content = f"export PYTHONPATH=./Assets/pyPackages\n" \
                           f"python3 {os.path.basename(run_script)}"

        self.user_files.add_asset_file(Asset(filename="run.sh", content=run_file_content))

        # Add the user script
        run_script = os.path.abspath(run_script)
        self.user_files.add_file(run_script)

        # Set the command
        self.command = "./run.sh"

    def __hash__(self):
        return hash(self.id)
