import json
import allure
import os
from functools import partial
from typing import Any, Dict
import pytest
from idmtools.assets import Asset, AssetCollection
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities import CommandLine
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_platform_comps.utils.scheduling import add_work_order, add_schedule_config, \
    default_add_schedule_config_sweep_callback
from idmtools_models.templated_script_task import TemplatedScriptTask, get_script_wrapper_unix_task, \
    LINUX_PYTHON_PATH_WRAPPER
from idmtools_platform_comps.utils.python_requirements_ac.requirements_to_asset_collection import \
    RequirementsToAssetCollection
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.common_experiments import wait_on_experiment_and_check_all_sim_status
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_platform_comps.utils.scheduling import default_add_workerorder_sweep_callback
from idmtools_test.utils.utils import get_case_name


@pytest.mark.comps
@pytest.mark.python
@allure.story("COMPS")
@allure.story("Python")
@allure.suite("idmtools_platform_comps")
@pytest.mark.serial
class TestWorkOrder(ITestWithPersistence):
    def setUp(self) -> None:
        self.case_name = get_case_name(os.path.basename(__file__) + "--" + self._testMethodName)
        print(self.case_name)
        self.platform = Platform('SlurmStage')

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

        ts = TemplatedSimulations(base_task=task)

        # use WorkOrder.json which override input commandline command and arguments
        add_work_order(ts, file_path=os.path.join(COMMON_INPUT_PATH, "scheduling", "slurm", "WorkOrder.json"))

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
        sb.add_sweep_definition(partial(default_add_workerorder_sweep_callback, file_name="WorkOrder.json"),
                                os.path.join(COMMON_INPUT_PATH, "scheduling", "slurm", "WorkOrder1.json"))

        ts.add_builder(sb)

        experiment = Experiment.from_template(ts, name=self.case_name)
        experiment.add_asset(os.path.join(COMMON_INPUT_PATH, "scheduling", "slurm", "commandline_model.py"))
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
        s1 = json.loads(workorder_content)
        s2 = json.loads("{\"Command\": \"python3 Assets/commandline_model.py 10000 10 100 1234\", \"NodeGroupName\": \"idm_cd\", \"NumCores\": 1, \"NumProcesses\": 1, \"NumNodes\": 1, \"Environment\": {\"key1\": \"value1\", \"key2\": \"value2\"}}")
        self.assertDictEqual(s1, s2)

    @pytest.mark.timeout(60)
    @pytest.mark.serial
    def test_wrapper_script_execute_comps(self):
        """
        To test wrapper task with WorkOrder.json. Comps will use Executable command from WorkOrder.json instead of
        wrapper command specified in the test
        Returns:

        """
        cmd = "python3.7 --version"
        task = CommandTask(cmd)

        task.common_assets.add_asset(
            Asset(relative_path=os.path.join("site-packages", "test-package"), filename="__init__.py",
                  content="a=\'123\'"))
        wrapper_task: TemplatedScriptTask = get_script_wrapper_unix_task(task,
                                                                         template_content=LINUX_PYTHON_PATH_WRAPPER)
        wrapper_task.script_binary = "/bin/bash"

        experiment = Experiment.from_task(wrapper_task, name=self.case_name)

        # upload WorkOrder.json to simulation root dir
        add_work_order(experiment, file_path=os.path.join("inputs", "WorkOrder.json"))

        wait_on_experiment_and_check_all_sim_status(self, experiment, self.platform, scheduling=True)
        self.assertTrue(experiment.succeeded)

        for sim in experiment.simulations:
            assets = self.platform._simulations.all_files(sim)
            for asset in assets:
                if asset.filename in ["stdout.txt"]:
                    content = asset.content.decode('utf-8').replace("\\\\", "\\")
                    # don't check full version in case comps updates system
                    self.assertIn('Python 3.7', content)

    def test_workorder_hpc(self):
        """
        To test workorder run in hpc cluster
        Returns:

        """
        task = JSONConfiguredPythonTask(
            script_path=os.path.join(COMMON_INPUT_PATH, "compsplatform", "working_model.py"),
            parameters=(dict(c=0)))

        experiment = Experiment.from_task(task, name=self.case_name)
        add_work_order(experiment, file_path=os.path.join(COMMON_INPUT_PATH, "scheduling", "hpc", "WorkOrder.json"))

        with Platform('Bayesian') as platform:
            experiment.run(wait_on_done=True, scheduling=True)
            self.assertTrue(experiment.succeeded)

        for sim in experiment.simulations:
            assets = platform._simulations.all_files(sim)
            for asset in assets:
                if asset.filename in ["stdout.txt"]:
                    content = asset.content.decode('utf-8').replace("\\\\", "\\")
                    self.assertIn('hello test', content)

    def test_workorder_environment(self):
        """
        To test python task with WorkOrder.json's environment. command in WorkOrder.json is python Assets/model.py
        in COMPS, file layout is:
        Assets-
              |_MyExternalLibarary
                       |_function.py
              |_model.py
              |_site-packages
                    |_numpy
        in order for model.py to call MyExternalLibarary.function which uses numpy package, MyExternalLibarary.function
        and numpy must be in PYTHONPATH
        So we add "PYTHONPATH": "$PYTHONPATH:$PWD/Assets:$PWD/Assets/site-packages" in WorkOrder.json

        Returns:
        """
        # add numpy package to cluster
        pl = RequirementsToAssetCollection(name=self.case_name, platform=self.platform, pkg_list=['numpy==1.19.5'])
        ac_id = pl.run()
        # add numpy to common_assets for a task
        common_assets = AssetCollection.from_id(ac_id, as_copy=True)
        # create task which generate config.json and upload script and assets
        task = JSONConfiguredPythonTask(
            script_path=os.path.join(COMMON_INPUT_PATH, "python", "model.py"), parameters=dict(a=1, b=10),
            envelope="parameters", common_assets=common_assets)

        # Add another folder to comps Assets
        task.common_assets.add_directory(assets_directory=os.path.join(COMMON_INPUT_PATH, "python", "Assets"))
        experiment = Experiment.from_task(task, name=self.case_name)
        # add local WorkOrder2.json to comps and change file name to WorkOrder.json
        add_work_order(experiment, file_path=os.path.join(COMMON_INPUT_PATH, "scheduling", "slurm", "WorkOrder2.json"))
        wait_on_experiment_and_check_all_sim_status(self, experiment, self.platform, scheduling=True)

        # only verify first simulation's stdout.txt
        files = self.platform.get_files(item=experiment.simulations[0], files=['stdout.txt'])
        stdout_content = files['stdout.txt'].decode('utf-8').replace("\\\\", "\\")
        stdout_content = stdout_content.replace("\\", "")
        self.assertIn("11", stdout_content)  # a+b = 1+10 = 11

    def test_schedule_config_pythontask(self):
        """
        To test python task with WorkOrder.json. Comps will use Executable command from WorkOrder.json instead of
        python task's command
        Returns:

        """
        # create task with script. here script doesn't matter. it will override by WorkOrder.json's command
        task = JSONConfiguredPythonTask(
            script_path=os.path.join(COMMON_INPUT_PATH, "compsplatform", "working_model.py"),
            parameters=(dict(c=0)))

        ts = TemplatedSimulations(base_task=task)

        # use dynamic WorkOrder.json which override input commandline command and arguments
        add_schedule_config(ts, command="python -c \"print('hello test')\"", node_group_name='idm_abcd', num_cores=2,
                            NumProcesses=1, NumNodes=1,
                            Environment={"key1": "value1", "key2": "value2"})

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

    def test_schedule_config_commandtask(self):
        """
        To test command task with WorkOrder.json. Comps will use Executable command from WorkOrder.json instead of
        command task's command specified in the test
        Returns:

        """

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
        sb.add_sweep_definition(
            partial(default_add_schedule_config_sweep_callback,
                    command="python3 Assets/commandline_model.py {pop_size} {pop_infected} {n_days} {rand_seed}",
                    node_group_name='idm_cd', num_cores=1),
            [dict(NumProcesses=1, NumNodes=1, Environment={"key1": "value1", "key2": "value2"})])

        ts.add_builder(sb)

        experiment = Experiment.from_template(ts, name=self.case_name)
        experiment.add_asset(os.path.join(COMMON_INPUT_PATH, "scheduling", "slurm", "commandline_model.py"))
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
        s1 = json.loads(workorder_content)
        s2 = json.loads("{\"Command\": \"python3 Assets/commandline_model.py 10000 10 100 1234\", \"NodeGroupName\": \"idm_cd\", \"NumCores\": 1, \"NumProcesses\": 1, \"NumNodes\": 1, \"Environment\": {\"key1\": \"value1\", \"key2\": \"value2\"}}")
        self.assertDictEqual(s1, s2)

    @pytest.mark.timeout(60)
    def test_schedule_config_with_wrapper_script_execute_comps(self):
        """
        To test wrapper task with WorkOrder.json. Comps will use Executable command from WorkOrder.json instead of
        wrapper command specified in the test
        Returns:

        """
        cmd = "python3.7 --version"
        task = CommandTask(cmd)

        task.common_assets.add_asset(
            Asset(relative_path=os.path.join("site-packages", "test-package"), filename="__init__.py",
                  content="a=\'123\'"))
        wrapper_task: TemplatedScriptTask = get_script_wrapper_unix_task(task,
                                                                         template_content=LINUX_PYTHON_PATH_WRAPPER)
        wrapper_task.script_binary = "/bin/bash"

        experiment = Experiment.from_task(wrapper_task, name=self.case_name)

        # upload dynamic WorkOrder.json to simulation root dir
        add_schedule_config(experiment, command="python3.7 --version", node_group_name='idm_abcd', num_cores=1,
                            NumProcesses=1, NumNodes=1, Environment={"key1": "value1", "key2": "value2"})

        wait_on_experiment_and_check_all_sim_status(self, experiment, self.platform, scheduling=True)
        self.assertTrue(experiment.succeeded)

        for sim in experiment.simulations:
            assets = self.platform._simulations.all_files(sim)
            for asset in assets:
                if asset.filename in ["stdout.txt"]:
                    content = asset.content.decode('utf-8').replace("\\\\", "\\")
                    # don't check full version in case comps updates system
                    self.assertIn('Python 3.7', content)

    def test_schedule_config_hpc(self):
        """
        To test workorder run in hpc cluster
        Returns:

        """
        task = JSONConfiguredPythonTask(
            script_path=os.path.join(COMMON_INPUT_PATH, "compsplatform", "working_model.py"),
            parameters=(dict(c=0)))

        experiment = Experiment.from_task(task, name=self.case_name)
        add_schedule_config(experiment, command="python -c \"print('hello test')\"", node_group_name='emod_abcd',
                            num_cores=1, SingleNode=False, Exclusive=False)

        with Platform('Bayesian') as platform:
            experiment.run(wait_on_done=True, scheduling=True)
            self.assertTrue(experiment.succeeded)

        for sim in experiment.simulations:
            assets = platform._simulations.all_files(sim)
            for asset in assets:
                if asset.filename in ["stdout.txt"]:
                    content = asset.content.decode('utf-8').replace("\\\\", "\\")
                    self.assertIn('hello test', content)

    def test_schedule_config_environment(self):
        """
        To test python task with WorkOrder.json's environment. command in WorkOrder.json is python Assets/model.py
        in COMPS, file layout is:
        Assets-
              |_MyExternalLibarary
                       |_function.py
              |_model.py
              |_site-packages
                    |_numpy
        in order for model.py to call MyExternalLibarary.function which uses numpy package, MyExternalLibarary.function
        and numpy must be in PYTHONPATH
        So we add "PYTHONPATH": "$PYTHONPATH:$PWD/Assets:$PWD/Assets/site-packages" in WorkOrder.json

        Returns:
        """
        # add numpy package to cluster
        pl = RequirementsToAssetCollection(name=self.case_name, platform=self.platform, pkg_list=['numpy==1.19.5'])
        ac_id = pl.run()
        # add numpy to common_assets for a task
        common_assets = AssetCollection.from_id(ac_id, as_copy=True)
        # create task which generate config.json and upload script and assets
        task = JSONConfiguredPythonTask(
            script_path=os.path.join(COMMON_INPUT_PATH, "python", "model.py"), parameters=dict(a=1, b=10),
            envelope="parameters", common_assets=common_assets)

        # Add another folder to comps Assets
        task.common_assets.add_directory(assets_directory=os.path.join(COMMON_INPUT_PATH, "python", "Assets"))
        experiment = Experiment.from_task(task, name=self.case_name)
        # add dynamic WorkOrder2.json to comps and change file name to WorkOrder.json
        add_schedule_config(experiment, command="python3 Assets/model.py", node_group_name='idm_abcd', num_cores=1,
                            NumProcesses=1, NumNodes=1,
                            Environment={"key1": "value1", "key2": "value2",
                                         "PYTHONPATH": "$PYTHONPATH:$PWD/Assets:$PWD/Assets/site-packages",
                                         "PATH": "$PATH:$PWD/Assets:$PWD/Assets/site-packages"})

        wait_on_experiment_and_check_all_sim_status(self, experiment, self.platform, scheduling=True)

        # only verify first simulation's stdout.txt
        files = self.platform.get_files(item=experiment.simulations[0], files=['stdout.txt'])
        stdout_content = files['stdout.txt'].decode('utf-8').replace("\\\\", "\\")
        stdout_content = stdout_content.replace("\\", "")
        self.assertIn("11", stdout_content)  # a+b = 1+10 = 11

    def test_workorder_in_workitem(self):
        """
          To test WorkItem's WorkOrder.json, user can dynamically pull docker image from idm's production artifactory directly
          instead of old way which had to deploy docker image to docker worker host machine
          in this example, we pull nyu dtk docker image to docker worker, then execute Eradication command in comps's
          WorkItem
          Returns:
          """
        command = "ls -lart"  # anything since it will be override with WorkOrder.json file
        from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem
        wi = SSMTWorkItem(name=self.case_name, command=command,tags={'idmtools': self.case_name})
        # overrode workorder.json with user provide file
        wi.load_work_order(os.path.join("inputs", "workitems", "ssmt", "WorkOrder.json"))
        wi.run(wait_on_done=True)
        out_filenames = ["stdout.txt"]
        files = self.platform.get_files(item=wi, files=out_filenames)
        stdout_content = files['stdout.txt'].decode('utf-8')
        self.assertIn("/dtk/Eradication version: 2.17.4463.0", stdout_content)

