from pathlib import Path
from time import time

import allure

import os

import pytest
from COMPS.Data import Experiment as COMPSExperiment
from COMPS.Data import Simulation as COMPSSimulation
from COMPS.Data import QueryCriteria

from idmtools.assets import AssetCollection
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask
from idmtools.utils.entities import save_id_as_file_as_hook

from idmtools_platform_comps.utils.general import update_item
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.shared_functions import validate_sim_tags
from idmtools_test.utils.utils import get_case_name

from idmtools_platform_comps.comps_platform import COMPSPlatform
from idmtools.entities.experiment import Experiment

from idmtools.entities.simulation import Simulation
from idmtools.registry.functions import FunctionPluginManager
from idmtools.registry.hook_specs import function_hook_impl


def register_plugins(name="Plugin_create_hook", **kwargs):
    """
    Register plugins.
    Args:
        name: Plugin name
        kwargs: user inputs
    Returns:
        None
    """
    # register plugins
    fpm = FunctionPluginManager.instance()
    fpm.register(Plugin_create_hook(**kwargs), name=name)


def un_register_plugins(name="Plugin_create_hook"):
    """
    Unregister plugins.
    Args:
        name: Plugin name
    Returns:
        None
    """
    fpm = FunctionPluginManager.instance()
    fpm.unregister(Plugin_create_hook(), name=name)


class Plugin_create_hook:
    """A 2nd hook implementation namespace."""

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    @function_hook_impl
    def idmtools_platform_pre_create_item(self, item, **kwargs):
        """
        This callback is called by the pre_create of each object type on a platform.
        An item can be a suite, workitem, simulation, asset collection or an experiment.
        Args:
            item: idmtools entity
        Returns:
            None
        """
        if isinstance(item, Experiment):
            item.tags.update({"tag_key": "tag_value"})

    @function_hook_impl
    def idmtools_platform_post_create_item(self, item, **kwargs):
        """
        This callback is called by the pre_create of each object type on a platform.
        An item can be a suite, workitem, simulation, asset collection or an experiment.
        Args:
            item: idmtools entity
        Returns:
            None
        """
        if isinstance(item, Simulation) and self.kwargs.get('my_test') == 1:
            item.tags.update({"sim_tag_post_key": "sim_tag_post_value"})

@pytest.mark.comps
@pytest.mark.python
@allure.story("COMPS")
@allure.story("Python")
@allure.suite("idmtools_platform_comps")
class TestHooks(ITestWithPersistence):
    def setUp(self) -> None:
        self.case_name = get_case_name(os.path.basename(__file__) + "--" + self._testMethodName)
        print(self.case_name)
        self.platform = Platform('SlurmStage')
        self.id_file = None

    def tearDown(self) -> None:
        try:
            os.remove(self.id_file)
        except:
            pass

    def test_simulation_hooks(self):
        base_task = CommandTask(command="python --version")
        sim = Simulation(task=base_task)

        exp = Experiment(name=self.case_name)
        exp.simulations = [sim]

        def add_exp_id_as_tag(item: Simulation, platform: 'COMPSPlatform'):
            item.tags['e_id'] = exp.id

        def update_tags(item: Simulation, platform: 'COMPSPlatform'):
            tags = {"a": 0}
            update_item(self.platform, item.id, ItemType.SIMULATION, tags)

        sim.add_pre_creation_hook(add_exp_id_as_tag)
        sim.add_post_creation_hook(update_tags)

        exp.run(wait_until_done=True)

        tag_value = "idmtools.entities.command_task.CommandTask"
        exp_tags = [{'e_id': exp.id, 'a': '0', 'task_type': tag_value}]
        validate_sim_tags(self, exp.id, exp_tags, tag_value)

    def test_experiment_pre_creation_hooks(self):
        base_task = CommandTask(command="python --version")
        sim = Simulation(task=base_task)

        exp = Experiment(name=self.case_name)
        exp.simulations = [sim]

        def add_pre_creation_hook(item: Experiment, platform: 'COMPSPlatform'):
            item.tags['pre_creation_tag'] = "pre_creation"

        exp.add_pre_creation_hook(add_pre_creation_hook)
        exp.pre_creation(self.platform)

        # validate exp has correct tag. Need to remove unrelated tags first
        exp.tags.pop('idmtools')
        exp.tags.pop("task_type")
        self.assertEqual(exp.tags, {'pre_creation_tag': 'pre_creation'})

    def test_experiment_post_creation_hooks(self):
        exp = Experiment(name=self.case_name)

        def add_post_creation_hook(item: Experiment, platform: 'COMPSPlatform'):
            item.tags['post_creation_tag'] = "post_creation"

        exp.add_post_creation_hook(add_post_creation_hook)
        exp.post_creation(self.platform)

        # validate exp has correct tag
        self.assertEqual(exp.tags, {'post_creation_tag': 'post_creation'})

    def test_experiment_pre_post_run_hooks(self):
        base_task = CommandTask(command="python --version")
        sim = Simulation(task=base_task)

        exp = Experiment(name=self.case_name)
        exp.simulations = [sim]

        def add_pre_run_hook(item: Experiment, platform: 'COMPSPlatform'):
            item.tags['pre_run_tag'] = "pre_run"

        def add_post_run_hook(item: Experiment, platform: 'COMPSPlatform'):
            item.tags['post_run_tag'] = "post_run"

        exp.add_pre_run_hook(add_pre_run_hook)
        exp.add_post_run_hook(add_post_run_hook)
        self.platform.run_items(exp)
        # validate exp has correct tag. Need to remove unrelated tags first
        exp.tags.pop('idmtools')
        exp.tags.pop("task_type")
        self.assertDictEqual(exp.tags, {'pre_run_tag': 'pre_run', 'post_run_tag': 'post_run'})

        # verify from comps experiment tags, note, post_run_hook tag will not show up in comps
        comps_tags = COMPSExperiment.get(exp.id, QueryCriteria().select_children('tags')).tags
        comps_tags.pop('idmtools')
        comps_tags.pop("task_type")
        self.assertDictEqual(comps_tags, {'pre_run_tag': 'pre_run'})

    def test_experiment_hooks(self):
        base_task = CommandTask(command="python --version")
        sim = Simulation(task=base_task)

        exp = Experiment(name=self.case_name)
        exp.simulations = [sim]

        def add_pre_creation_hook(item: Experiment, platform: 'COMPSPlatform'):
            item.tags['pre_creation_tag'] = "pre_creation"

        def add_post_creation_hook(item: Experiment, platform: 'COMPSPlatform'):
            tags = {"post_creation_tag": "post_creation"}
            update_item(platform, item.id, ItemType.EXPERIMENT, tags)

        def add_pre_run_hook(item: Experiment, platform: 'COMPSPlatform'):
            item.tags['pre_run_tag'] = "pre_run"

        exp.add_pre_creation_hook(add_pre_creation_hook)
        exp.add_post_creation_hook(add_post_creation_hook)
        exp.add_pre_run_hook(add_pre_run_hook)
        exp.add_post_run_hook(save_id_as_file_as_hook)

        exp.run(wait_until_done=True)
        tag_value = "idmtools.entities.command_task.CommandTask"
        expected_tags = {'pre_creation_tag': 'pre_creation', 'post_creation_tag': 'post_creation',
                         'pre_run_tag': 'pre_run',
                         'task_type': tag_value}

        # verify tags from comps are expected
        tags = COMPSExperiment.get(exp.id, QueryCriteria().select_children('tags')).tags
        tags.pop('idmtools')
        self.assertDictEqual(tags, expected_tags)

        # verify we saved file from post_run_kko
        id_file = Path(f'{exp.item_type}.{exp.name}.id')
        with open(id_file, 'r') as file:
            content = file.read()
            self.assertEqual(content, exp.id + "::Experiment")
        self.id_file = id_file

    def test_assetcollection_creation_hook(self):
        input_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inputs")
        ran_at = str(time())
        ac = AssetCollection([os.path.join(input_file_path, "hello.py")])

        def add_date_as_tag(ac: AssetCollection, platform: 'COMPSPlatform'):
            ac.tags['date'] = ran_at

        def add_post_tag(ac: AssetCollection, platform: 'COMPSPlatform'):
            ac.tags['post_tag'] = "post_tag"

        ac.add_pre_creation_hook(add_date_as_tag)
        ac.add_post_creation_hook(add_post_tag)

        result = self.platform.create_items(ac)
        print(result[0].id)
        # verify that assetcollection get updated for tags from pre and post create hook function
        ac_comps = self.platform.get_item(result[0].id, item_type=ItemType.ASSETCOLLECTION, raw=True)
        self.assertEqual(result[0].tags['date'], ran_at)
        self.assertEqual(result[0].tags['post_tag'], "post_tag")
        self.assertEqual(ac_comps.tags['date'], ran_at)
        self.assertIsNotNone(ac_comps.tags['idmtools'])
        self.assertEqual(ac_comps.tags.__len__(), 2)  # ac_comps only has 2 tags, there is no post_tag

    def test_plugin_hooks(self):
        base_task = CommandTask(command="python --version")
        sim = Simulation(task=base_task)

        exp = Experiment(name=self.case_name)
        exp.simulations = [sim]
        kwargs = {"my_test": 1}

        register_plugins(**kwargs)
        exp.run(True)
        # verify idmtools experiment tags
        expected_tags = {'tag_key': 'tag_value'}
        exp.tags.pop('idmtools')
        exp.tags.pop('task_type')
        self.assertDictEqual(exp.tags, expected_tags)
        exp.simulations[0].tags.pop('task_type')
        self.assertDictEqual(exp.simulations[0].tags, {'sim_tag_post_key': 'sim_tag_post_value'})
        # verify comps experiment tag should contain only pre_create tag
        # and simulation does not contain post tags
        comps_tags = COMPSExperiment.get(exp.id, QueryCriteria().select_children('tags')).tags
        comps_tags.pop('idmtools')
        comps_tags.pop("task_type")
        self.assertDictEqual(comps_tags, expected_tags)
        sim_tags = COMPSSimulation.get(exp.simulations[0].id, QueryCriteria().select_children('tags')).tags
        sim_tags.pop('task_type')
        self.assertDictEqual(sim_tags, {})
        un_register_plugins()

