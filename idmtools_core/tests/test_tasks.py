import allure
import os
from unittest import TestCase

import pytest
from idmtools.assets import Asset, AssetCollection
from idmtools.core.platform_factory import Platform
from idmtools.entities import CommandLine
from idmtools.entities.command_task import CommandTask
from idmtools.entities.simulation import Simulation


@pytest.mark.tasks
@pytest.mark.smoke
@allure.story("Tasks")
@allure.suite("idmtools_core")
class TestTasks(TestCase):

    def test_command_requires_command(self):
        with self.assertRaises(ValueError) as ex:
            task = CommandTask()  # noqa F841
        self.assertEqual("Command is required", ex.exception.args[0])

    def test_command_init_from_str_(self):
        example_command, task = self.get_ls_command_task()
        self.assertEqual(task.command.cmd, example_command)

    def test_command_line_from_str(self):
        cmd = "ls -al"
        cl = CommandLine(cmd)
        self.assertEqual(cl.cmd, cmd)

    @staticmethod
    def get_ls_command_task():
        example_command = 'ls -al'
        task = CommandTask(command=example_command)
        return example_command, task

    @staticmethod
    def get_cat_command():
        task = CommandTask(command='cat pytest.ini')
        task.common_assets.add_asset(Asset(absolute_path=os.path.join(os.path.dirname(__file__), './pytest.ini')))
        return task

    # TODO fix as part of rewrite of tasks
    # def test_command_is_required(self):
    #     with self.assertRaises(ValueError) as e:
    #         task = CommandTask()
    #         task.on_simulation_prep(Simulation(task=task))
    #     self.assertEqual(str(e.exception), 'Command is required for on task when preparing an experiment')

    def test_assets_on_tasks(self):
        task = self.get_cat_command()

        self.assertIn(task.common_assets.assets[0].absolute_path, os.path.join(os.path.dirname(__file__), './pytest.ini'))

    def test_command_task_custom_hooks(self):
        global test_global
        global platform_item
        task = self.get_cat_command()
        test_global = 0
        platform_item = None

        def update_x_callback(task):  # noqa F841
            global test_global
            test_global += 1

            return AssetCollection()
        task.gather_common_asset_hooks.append(update_x_callback)
        task.gather_common_assets()
        self.assertEqual(test_global, 1)

        def update_sim(simulation, platform):
            global platform_item
            platform_item = platform
            simulation.tags['a'] = 12
        task.add_pre_creation_hook(update_sim)
        sim = Simulation(task=task)
        p = Platform('Test')
        task.pre_creation(sim, Platform('Test'))
        self.assertEqual(sim.tags['a'], 12)
        # Note, due to new bug fix for platform uid(in iitem.py), we can not longer compare 2 platforms equal as before.
        # We used to have _uid member in platform which was comparison field and always None. Now, it has value with bug
        # fix. So in order to compare 2 platforms equal, let's ignore this property and compare rest of members
        platform_item.uid = None
        p.uid = None
        self.assertEqual(platform_item, p)
