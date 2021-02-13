import allure
import json
import os
from functools import partial
from typing import Any, Dict

import pytest

from idmtools.assets import Asset
from idmtools.builders import SimulationBuilder
from idmtools.core import ItemType

from idmtools.core.platform_factory import Platform
from idmtools.entities import CommandLine
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_models.templated_script_task import TemplatedScriptTask, get_script_wrapper_unix_task, \
    LINUX_PYTHON_PATH_WRAPPER, get_script_wrapper_windows_task, WINDOWS_PYTHON_PATH_WRAPPER
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.common_experiments import wait_on_experiment_and_check_all_sim_status
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence

@pytest.mark.comps
@pytest.mark.python
@allure.story("COMPS")
@allure.story("Python")
@allure.suite("idmtools_platform_comps")
class TestWorkOrder(ITestWithPersistence):
    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)
        self.platform = Platform('SLURM2')

    def test_workorder_pythontask(self):
        """
        To test python task with WorkOrder.json. Comps will use Executable command from WorkOrder.json instead of
        python task's command
        Returns:

        """
        # create task with script. here script doesn't matter. it will override by WorkOrder.json's command
        task = JSONConfiguredPythonTask(
            script_path=os.path.join(COMMON_INPUT_PATH, "compsplatform", "working_model.py"),
            parameters=(dict(c=0)))

        # use WorkOrder.json which override input commandline command and arguments
        task.transient_assets.add_asset(os.path.join(COMMON_INPUT_PATH, "scheduling", "slurm", "WorkOrder.json"))

        ts = TemplatedSimulations(base_task=task)
        builder = SimulationBuilder()

        def param_update(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
            return simulation.task.set_parameter(param, value)

        builder.add_sweep_definition(partial(param_update, param="a"), range(3))
        ts.add_builder(builder)

        experiment = Experiment.from_template(ts, name=self.case_name)
        wait_on_experiment_and_check_all_sim_status(self, experiment, self.platform, scheduling=True)
        self.assertTrue(experiment.succeeded)
        for sim in experiment.simulations:
            assets = self.platform._simulations.all_files(sim)
            for asset in assets:
                if asset.filename in ["stdout.txt"]:
                    content = asset.content.decode('utf-8').replace("\\\\", "\\")
                    self.assertIn('hello test', content)

    def test_workorder_commandtask(self):
        """
        To test command task with WorkOrder.json. Comps will use Executable command from WorkOrder.json instead of
        command task's command specified in the test
        Returns:

        """
        def add_file(simulation, file_name, file_path):
            with open(file_path, "r") as jsonFile:
                data = json.loads(jsonFile.read())
            data["Command"] = simulation.task.command.cmd
            simulation.task.transient_assets.add_asset(Asset(filename=file_name, content=json.dumps(data)))

        def set_value(simulation, name, value):
            fix_value = round(value, 2) if isinstance(value, float) else value
            # add argument
            simulation.task.command.add_raw_argument(str(fix_value))
            # add tag with our value
            simulation.tags[name] = fix_value

        # create commandline input for the task
        command = CommandLine("python3 Assets/commandline_model.py")
        task = CommandTask(command=command)
        ts = TemplatedSimulations(base_task=task)

        sb = SimulationBuilder()
        sb.add_sweep_definition(partial(set_value, name="pop_size"), [10000, 20000])
        sb.add_sweep_definition(partial(set_value, name="pop_infected"), [10, 100])
        sb.add_sweep_definition(partial(set_value, name="n_days"), [100, 110])
        sb.add_sweep_definition(partial(set_value, name="rand_seed"), [1234, 4567])
        sb.add_sweep_definition(partial(add_file, file_name="WorkOrder.json"),
                                os.path.join(COMMON_INPUT_PATH, "scheduling", "slurm", "WorkOrder1.json"))

        ts.add_builder(sb)

        experiment = Experiment.from_template(ts, name=self.case_name)
        experiment.add_asset(os.path.join(COMMON_INPUT_PATH, "scheduling", "slurm", "commandline_model.py"))
        # self.platform.set_core_scheduling()
        wait_on_experiment_and_check_all_sim_status(self, experiment, self.platform, scheduling=True)
        self.assertTrue(experiment.succeeded)

        # only verify first simulation's stdout.txt
        files = self.platform.get_files(item=experiment.simulations[0], files=['stdout.txt', 'WorkOrder.json'])
        stdout_content = files['stdout.txt'].decode('utf-8').replace("\\\\", "\\")
        stdout_content = stdout_content.replace("\\", "")
        self.assertIn(
            "{'pop_size': '10000', 'pop_infected': '10', 'n_days': 100, 'rand_seed': '1234', 'pop_type': 'hybrid'}",
            stdout_content)

        workorder_content = files['WorkOrder.json'].decode('utf-8').replace("\\\\", "\\")
        self.assertEqual(workorder_content,
                         "{\"Command\": \"python3 Assets/commandline_model.py 10000 10 100 1234\", \"NodeGroupName\": \"idm_cd\", \"NumCores\": 1, \"NumProcesses\": 1, \"NumNodes\": 1, \"Environment\": {\"key1\": \"value1\", \"key2:\": \"value2\"}}")

    @pytest.mark.timeout(60)
    def test_wrapper_script_execute_comps(self):
        """
        To test wrapper task with WorkOrder.json. Comps will use Executable command from WorkOrder.json instead of
        wrapper command specified in the test
        Returns:

        """
        cmd = "python3.6 --version"
        task = CommandTask(cmd)

        task.common_assets.add_asset(
            Asset(relative_path=os.path.join("site-packages", "test-package"), filename="__init__.py",
                  content="a=\'123\'"))
        wrapper_task: TemplatedScriptTask = get_script_wrapper_unix_task(task,
                                                                         template_content=LINUX_PYTHON_PATH_WRAPPER)
        wrapper_task.script_binary = "/bin/bash"
        # upload WorkOrder.json to simulation root dir
        wrapper_task.transient_assets.add_asset(os.path.join("inputs", "WorkOrder.json"))
        experiment = Experiment.from_task(wrapper_task, name=self.case_name)
        # self.platform.set_core_scheduling()
        wait_on_experiment_and_check_all_sim_status(self, experiment, self.platform, scheduling=True)
        self.assertTrue(experiment.succeeded)

        for sim in experiment.simulations:
            assets = self.platform._simulations.all_files(sim)
            for asset in assets:
                if asset.filename in ["stdout.txt"]:
                    content = asset.content.decode('utf-8').replace("\\\\", "\\")
                    # don't check full version in case comps updates system
                    self.assertIn('Python 3.6', content)

    def test_workorder_hpc(self):
        """
        To test workorder run in hpc cluster
        Returns:

        """
        task = JSONConfiguredPythonTask(
            script_path=os.path.join(COMMON_INPUT_PATH, "compsplatform", "working_model.py"),
            parameters=(dict(c=0)))

        task.transient_assets.add_asset(os.path.join(COMMON_INPUT_PATH, "scheduling", "hpc", "WorkOrder.json"))

        experiment = Experiment.from_task(task, name=self.case_name)
        with Platform('COMPS2') as platform:
            # platform.set_core_scheduling()
            experiment.run(wait_on_done=True, scheduling=True)
            self.assertTrue(experiment.succeeded)

        for sim in experiment.simulations:
            assets = platform._simulations.all_files(sim)
            for asset in assets:
                if asset.filename in ["stdout.txt"]:
                    content = asset.content.decode('utf-8').replace("\\\\", "\\")
                    self.assertIn('hello test', content)
