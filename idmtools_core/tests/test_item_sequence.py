import json
import os
import unittest.mock
from functools import partial

import allure
import pytest
from pathlib import Path

from idmtools import IdmConfigParser
from idmtools.core.platform_factory import Platform
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_platform_slurm.platform_operations.utils import add_dammy_suite
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.test_task import TestTask
from idmtools.entities.experiment import Experiment


@pytest.mark.assets
@pytest.mark.smoke
@allure.story("Entities")
@allure.story("Plugins")
@allure.suite("idmtools_core")
class TestItemSequence(unittest.TestCase):
    def test_id_generator_error(self):
        platform = Platform('Test')
        tt = TestTask()
        s = Simulation(task=tt)
        e = Experiment()
        e.simulations.append(s)

        parser = IdmConfigParser()
        parser._load_config_file(file_name='idmtools_uuid_error.ini')
        parser.ensure_init(file_name='idmtools_uuid_error.ini', force=True)

        id_gen = parser.get_option(None, 'id_generator')
        self.assertEqual(id_gen, 'abcdefg')
        with self.assertRaises(RuntimeError) as r:
            platform = Platform('Test')
        self.assertIn("Could not find the id plugin idmtools_id_generate_abcdefg defined by ", r.exception.args[0])
        self.assertIn("idmtools_id_generate_item_sequence, idmtools_id_generate_uuid", r.exception.args[0])

    def test_id_item_sequence_no_config(self):
        parser = IdmConfigParser()
        config_ini = 'idmtools_item_sequence_no_config.ini'
        parser._load_config_file(file_name=config_ini)
        parser.ensure_init(file_name=config_ini, force=True)
        sequence_file = self.get_sequence_file()

        tt = TestTask()
        self.assertFalse(sequence_file.exists())
        s = Simulation(task=tt)
        self.assertEqual(s.id, "Simulation0000000")

    @staticmethod
    def get_sequence_file():
        sequence_file = Path(IdmConfigParser.get_option("item_sequence", "sequence_file", 'item_sequences.json')).expanduser()
        if sequence_file.exists():
            sequence_file.unlink()
        return sequence_file

    def test_id_item_sequence(self):
        parser = IdmConfigParser()
        parser._load_config_file(file_name='idmtools_item_sequence.ini')
        parser.ensure_init(file_name='idmtools_item_sequence.ini', force=True)
        sequence_file = self.get_sequence_file()

        tt = TestTask()
        self.assertFalse(sequence_file.exists())
        s = Simulation(task=tt)
        self.assertEqual(s.id, "Simulation000000")
        self.assertTrue(sequence_file.exists())
        e = Experiment(name='Test Sequential IDs')
        self.assertTrue(e.id, "Experiment000000")
        platform = Platform('Test', missing_ok=True)

        e2 = Experiment(name='Test2')
        self.assertEqual(e2.id, "Experiment000001")
        s2 = Simulation(task=tt)
        self.assertEqual(s2.id, "Simulation000001")

        with open(sequence_file, 'r') as file:
            seq = json.load(file)
            exp_num = seq['Experiment']
            sim_num = seq['Simulation']

            self.assertEqual(e2.id, 'Experiment00000' + f'{exp_num}')
            self.assertEqual(s2.id, 'Simulation00000' + f'{sim_num}')
            self.assertEqual(seq['Unknown'], 0)

    def test_perf(self):
        platform = Platform('TestExecute', missing_ok=True)
        parser = IdmConfigParser()
        parser._load_config_file(file_name='idmtools_slurm.ini')
        task = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"),
                                        envelope="parameters", parameters=(dict(c=0)))
        ts = TemplatedSimulations(base_task=task)
        e = Experiment.from_template(ts)
        from idmtools.builders import SimulationBuilder
        builder = SimulationBuilder()

        def param_update(simulation, param, value):
            return simulation.task.set_parameter(param, value)

        builder.add_sweep_definition(partial(param_update, param="a"), range(30))
        builder.add_sweep_definition(partial(param_update, param="b"), range(50))
        e.simulations.add_builder(builder)
        e.run(wait_until_done=True)

    def test_id(self):
        parser = IdmConfigParser()
        parser._load_config_file(file_name='idmtools_slurm.ini')
        parser.ensure_init(file_name='idmtools_slurm.ini', force=True)
        sequence_file = self.get_sequence_file()
        task = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, "python", "model3.py"),
                                        envelope="parameters", parameters=(dict(c=0)))
        platform = Platform('TestExecute', missing_ok=True)
        ts = TemplatedSimulations(base_task=task)
        e = Experiment.from_template(ts)
        from idmtools.builders import SimulationBuilder
        builder = SimulationBuilder()

        def param_update(simulation, param, value):
            return simulation.task.set_parameter(param, value)

        builder.add_sweep_definition(partial(param_update, param="a"), range(3))
        builder.add_sweep_definition(partial(param_update, param="b"), range(3))
        e.simulations.add_builder(builder)
        simulations = e.simulations.items
        print("Before run")
        [print(sim.id) for sim in simulations]
        #suite = add_dammy_suite(e)
        #suite.run(platform=platform, dry_run=True, wait_until_done=False, wait_on_done=False)
        e.run(wait_until_done=True)
        print("After run")
        simulations = e.simulations.items
        [print(sim.id) for sim in simulations]