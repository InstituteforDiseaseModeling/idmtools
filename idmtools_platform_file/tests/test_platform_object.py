import os
import shutil
from contextlib import suppress
from pathlib import PurePath
from zipfile import ZipFile
import allure
import pytest
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_platform_file.file_platform import FilePlatform
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.decorators import linux_only
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.utils import get_case_name

CP = PurePath(COMMON_INPUT_PATH)
OUTPUT_PATH = PurePath(__file__).parent.joinpath(".file_platform_out")


@pytest.mark.file_platform
@allure.story("FilePlatform")
@allure.suite("idmtools_platform_files")
class TestFilePlatform(ITestWithPersistence):
    def setUp(self) -> None:
        super().setUp()
        self.platform: FilePlatform = Platform("File", output_directory=OUTPUT_PATH, missing_ok=True)
        self.case_name = get_case_name(os.path.basename(__file__) + "--" + self._testMethodName)
        with suppress(OSError):
            shutil.rmtree(OUTPUT_PATH)

    def test_json_experiment_archive(self):
        experiment = self.get_json_experiment(50)
        experiment.run(wait_until_done=True, platform=self.platform, is_archive=True)
        self.assertTrue(experiment.done)
        self.assertTrue(experiment.succeeded)

        e_path = OUTPUT_PATH.joinpath(f'{experiment.name}0')
        self.assertTrue(os.path.exists(e_path), msg=f"{e_path} does not exist")

        a_path = e_path.joinpath("Assets")
        self.assertTrue(os.path.exists(a_path))

        archive = e_path.joinpath('simulations.zip')
        self.assertTrue(os.path.exists(archive), msg=f"{archive} does not exist")

        with ZipFile(archive, 'r') as zf:
            infos = zf.infolist()

            dirs = {str(PurePath(info.filename).parent) for info in infos}
            for i in range(50):
                sp = f"{i}"
                self.assertTrue(sp in dirs)

    def get_json_experiment(self, total: int):
        model_path = CP.joinpath(COMMON_INPUT_PATH, "compsplatform", 'mixed_model.py')
        task = JSONConfiguredPythonTask(script_path=model_path)
        builder = SimulationBuilder()
        builder.add_sweep_definition(JSONConfiguredPythonTask.set_parameter_partial('P'), range(total))
        experiment = Experiment.from_builder(builder, task, name=self.case_name)
        return experiment

    def test_json_experiment(self):
        self.platform.write_scripts = True
        experiment = self.get_json_experiment(10)
        experiment.run(wait_until_done=True, platform=self.platform, is_archive=False)
        self.assertTrue(experiment.done)
        self.assertTrue(experiment.succeeded)

        e_path = OUTPUT_PATH.joinpath(f'{experiment.name}0')
        self.assertTrue(os.path.exists(e_path), msg=f"{e_path} does not exist")

        a_path = e_path.joinpath("Assets")
        self.assertTrue(os.path.exists(a_path))

        for i in range(10):
            sd = e_path.joinpath(f"{i}")
            self.assertTrue(os.path.exists(sd))
            self.assertTrue(os.path.exists(sd.joinpath("config.json")))
            self.assertTrue(os.path.exists(sd.joinpath("simulation_metadata.json")))
            self.assertTrue(os.path.exists(sd.joinpath("run.sh")))

        self.platform.write_scripts = False

    def test_json_experiment_no_script(self):
        self.platform.write_scripts = False
        experiment = self.get_json_experiment(10)
        experiment.run(wait_until_done=True, platform=self.platform, is_archive=False)
        self.assertTrue(experiment.done)
        self.assertTrue(experiment.succeeded)

        e_path = OUTPUT_PATH.joinpath(f'{experiment.name}0')
        self.assertTrue(os.path.exists(e_path), msg=f"{e_path} does not exist")

        a_path = e_path.joinpath("Assets")
        self.assertTrue(os.path.exists(a_path))

        for i in range(10):
            sd = e_path.joinpath(f"{i}")
            self.assertTrue(os.path.exists(sd))
            self.assertTrue(os.path.exists(sd.joinpath("config.json")))
            self.assertTrue(os.path.exists(sd.joinpath("simulation_metadata.json")))

    def test_json_experiment_copy_experiment(self):
        self.platform.copy_experiment_assets = True
        experiment = self.get_json_experiment(10)
        experiment.run(wait_until_done=True, platform=self.platform, is_archive=False)
        self.assertTrue(experiment.done)
        self.assertTrue(experiment.succeeded)

        e_path = OUTPUT_PATH.joinpath(f'{experiment.name}0')
        self.assertTrue(os.path.exists(e_path), msg=f"{e_path} does not exist")

        a_path = e_path.joinpath("Assets")
        self.assertTrue(os.path.exists(a_path))

        for i in range(10):
            sd = e_path.joinpath(f"{i}")
            self.assertTrue(os.path.exists(sd))
            self.assertTrue(os.path.exists(sd.joinpath("Assets")))
            self.assertTrue(os.path.isdir(sd.joinpath("Assets")))
            self.assertTrue(os.path.exists(sd.joinpath("config.json")))
            self.assertTrue(os.path.exists(sd.joinpath("simulation_metadata.json")))
        self.platform.copy_experiment_assets = False

    @linux_only
    def test_json_experiment_link(self):
        self.platform.use_links = True
        experiment = self.get_json_experiment(10)
        experiment.run(wait_until_done=True, platform=self.platform, is_archive=False)
        self.assertTrue(experiment.done)
        self.assertTrue(experiment.succeeded)

        e_path = OUTPUT_PATH.joinpath(f'{experiment.name}0')
        self.assertTrue(os.path.exists(e_path), msg=f"{e_path} does not exist")

        a_path = e_path.joinpath("Assets")
        self.assertTrue(os.path.exists(a_path))

        for i in range(10):
            sd = e_path.joinpath(f"{i}")
            self.assertTrue(os.path.exists(sd))
            self.assertTrue(os.path.exists(sd.joinpath("Assets")))
            self.assertTrue(os.path.islink(sd.joinpath("Assets")))
            self.assertTrue(os.path.exists(sd.joinpath("config.json")))
            self.assertTrue(os.path.exists(sd.joinpath("simulation_metadata.json")))
