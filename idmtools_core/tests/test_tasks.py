import os
from unittest import TestCase
import pytest
from idmtools.assets import Asset
from idmtools.entities.command_task import CommandTask
from idmtools.entities.simulation import Simulation


@pytest.mark.tasks
class TestTasks(TestCase):

    def test_command_init_from_str_(self):
        example_command, task = self.get_ls_command_task()
        self.assertEqual(task.command.cmd, example_command)

    @staticmethod
    def get_ls_command_task():
        example_command = 'ls -al'
        task = CommandTask(command=example_command)
        return example_command, task

    @staticmethod
    def get_cat_command():
        task = CommandTask(command='cat pytest.ini')
        task.add_asset(Asset('./pytest.ini'))
        return task

    def test_command_is_required(self):
        with self.assertRaises(ValueError) as e:
            task = CommandTask()
        self.assertEqual(str(e.exception), 'Command is required')

    def test_assets_on_tasks(self):
        task = self.get_cat_command()

        self.assertIn(task.assets.assets[0].absolute_path, os.path.join(os.path.dirname(__file__), './pytest.ini'))

    def test_command_task_custom_hooks(self):
        global test_global
        task = self.get_cat_command()
        test_global = 0

        def update_x_callback():
            global test_global
            test_global += 1
        task.gather_asset_hooks.append(update_x_callback)
        task.gather_assets()
        self.assertEqual(test_global, 1)

        def update_sim(simulation):
            simulation.tags['a'] = 12
        task.init_hooks.append(update_sim)
        sim = Simulation(task=task)
        task.init(sim)
        self.assertEqual(sim.tags['a'], 12)
