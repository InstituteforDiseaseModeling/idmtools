import json
import time
import unittest.mock
from functools import partial
import allure
import pytest
from pathlib import Path
from idmtools import IdmConfigParser
from idmtools.core.platform_factory import Platform
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.test_execute_platform import clear_execute_platform
from idmtools_test.utils.test_task import TestTask
from idmtools.entities.experiment import Experiment
from idmtools_test.utils.utils import get_performance_scale, clear_id_cache


@pytest.mark.serial
@pytest.mark.assets
@pytest.mark.smoke
@allure.story("Entities")
@allure.story("Plugins")
@allure.suite("idmtools_core")
class TestItemSequence(unittest.TestCase):

    def setUp(self):
        self.get_sequence_file()
        clear_execute_platform()

    @classmethod
    def tearDownClass(cls) -> None:
        clear_id_cache()
        clear_execute_platform()

    def test_id_generator_error(self):
        clear_id_cache()

        parser = IdmConfigParser()
        parser._load_config_file(file_name='idmtools_uuid_error.ini')
        parser.ensure_init(file_name='idmtools_uuid_error.ini', force=True)

        id_gen = parser.get_option(None, 'id_generator')
        self.assertEqual(id_gen, 'abcdefg')
        with self.assertRaises(RuntimeError) as r:
            platform = Platform('Test')
            tt = TestTask()
            s = Simulation(task=tt)
            e = Experiment()
            e.simulations.append(s)
        self.assertIn("Could not find the id plugin idmtools_id_generate_abcdefg defined by ", r.exception.args[0])
        self.assertIn("idmtools_id_generate_item_sequence, idmtools_id_generate_uuid", r.exception.args[0])

    def test_id_item_sequence_no_config(self):
        clear_id_cache()
        parser = IdmConfigParser()
        config_ini = 'idmtools_item_sequence_no_config.ini'
        parser._load_config_file(file_name=config_ini)
        parser.ensure_init(file_name=config_ini, force=True)
        sequence_file = self.get_sequence_file()

        self.assertFalse(sequence_file.exists())
        s = Simulation(task=TestTask())
        self.assertEqual(s.id, "Simulation0000000")

    @staticmethod
    def get_sequence_file():
        sequence_file = Path(IdmConfigParser.get_option("item_sequence", "sequence_file", Path().home().joinpath(".idmtools", "itemsequence", "index.json")))
        if sequence_file.exists():
            sequence_file.unlink()
        return sequence_file

    def test_id_item_sequence(self):
        clear_id_cache()
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
        platform = Platform('TestExecute', type='TestExecute')

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

    @pytest.mark.serial
    @pytest.mark.performance
    def test_local_execute_perf(self):
        clear_id_cache()

        parser = IdmConfigParser()
        parser._load_config_file(file_name='idmtools_item_sequence_no_config.ini')

        start_time_a = time.time()
        self._run_experiment()
        start_time_b = time.time()
        run_time_a = start_time_b - start_time_a

        # Reset to uuid generation and run again
        IdmConfigParser.clear_instance()
        clear_id_cache()

        parser = IdmConfigParser()
        parser._load_config_file(file_name='idmtools.ini')

        start_time_c = time.time()
        self._run_experiment()
        start_time_d = time.time()

        # compare run times
        run_time_b = start_time_d - start_time_c
        self.assertTrue(run_time_a <= run_time_b or (run_time_a - run_time_b) > (run_time_b * .10))

    @pytest.mark.serial
    @pytest.mark.performance
    def test_local_execute_perf_with_template(self):
        clear_id_cache()

        parser = IdmConfigParser()
        parser._load_config_file(file_name='idmtools_item_sequence.ini')

        start_time_a = time.time()
        self._run_experiment()
        start_time_b = time.time()
        run_time_a = start_time_b - start_time_a

        # Reset to uuid generation
        IdmConfigParser.clear_instance()
        clear_id_cache()

        parser = IdmConfigParser()
        parser._load_config_file(file_name='idmtools.ini')

        start_time_c = time.time()
        self._run_experiment()
        start_time_d = time.time()
        run_time_b = start_time_d - start_time_c

        # compare run times
        self.assertTrue(run_time_a <= run_time_b or (run_time_a - run_time_b) > (run_time_b * .10))

    def _run_experiment(self, ):
        platform = Platform('TestExecute', type='TestExecute')

        task = task = TestTask()
        ts = TemplatedSimulations(base_task=task)
        e = Experiment.from_template(ts)
        from idmtools.builders import SimulationBuilder
        builder = SimulationBuilder()

        def param_update(simulation, param, value):
            return simulation.task.set_parameter(param, value)

        builder.add_sweep_definition(partial(param_update, param="a"), range(10 * get_performance_scale()))
        builder.add_sweep_definition(partial(param_update, param="b"), range(50))
        e.simulations.add_builder(builder)
        e.run(wait_until_done=True)
        return

    @pytest.mark.serial
    def test_id(self):
        clear_id_cache()
        parser = IdmConfigParser()
        parser._load_config_file(file_name='idmtools_item_sequence.ini')
        parser.ensure_init(file_name='idmtools_item_sequence.ini', force=True)
        sequence_file = self.get_sequence_file()
        mp = Path(COMMON_INPUT_PATH).joinpath("python").joinpath("model3.py")
        task = TestTask()
        platform = Platform('TestExecute', type='TestExecute')
        ts = TemplatedSimulations(base_task=task)
        e = Experiment.from_template(ts)
        from idmtools.builders import SimulationBuilder
        builder = SimulationBuilder()

        def param_update(simulation, param, value):
            return simulation.task.set_parameter(param, value)

        builder.add_sweep_definition(partial(param_update, param="a"), range(3))
        builder.add_sweep_definition(partial(param_update, param="b"), range(3))
        e.simulations.add_builder(builder)
        e.assets.add_asset(str(mp))
        e.simulations = [s for s in e.simulations]
        e.gather_common_assets_from_task = False

        pre_run = e.simulations.items
        e.run(wait_until_done=True)
        post_run = e.simulations.items
        self.assertEqual(pre_run, post_run)

    @pytest.mark.serial
    def test_seq_file_backup(self):
        clear_id_cache()
        parser = IdmConfigParser()
        parser._load_config_file(file_name='idmtools_default_location.ini')
        parser.ensure_init(file_name='idmtools_default_location.ini', force=True)
        sequence_file = self.get_sequence_file()
        mp = Path(COMMON_INPUT_PATH).joinpath("python").joinpath("model3.py")
        task = TestTask()
        platform = Platform('TestExecute', type='TestExecute')
        ts = TemplatedSimulations(base_task=task)
        e = Experiment.from_template(ts)
        from idmtools.builders import SimulationBuilder
        builder = SimulationBuilder()

        def param_update(simulation, param, value):
            return simulation.task.set_parameter(param, value)

        builder.add_sweep_definition(partial(param_update, param="a"), range(3))
        builder.add_sweep_definition(partial(param_update, param="b"), range(3))
        e.simulations.add_builder(builder)


        with platform:
            e.run(wait_until_done=True)

        f = open(sequence_file)
        bak = open(f'{sequence_file}.bak')
        sequence_file_json = json.load(f)
        backup_file_json = json.load(bak)
        self.assertEqual(sequence_file_json, backup_file_json)