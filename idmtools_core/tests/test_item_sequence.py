import json
import unittest.mock
import allure
import pytest
from pathlib import Path

from idmtools import IdmConfigParser
from idmtools.core.platform_factory import Platform
from idmtools.entities.simulation import Simulation
from idmtools_test.utils.test_task import TestTask
from idmtools.entities.experiment import Experiment


@pytest.mark.assets
@pytest.mark.smoke
@allure.story("Entities")
@allure.story("Plugins")
@allure.suite("idmtools_core")
class TestItemSequence(unittest.TestCase):
    def test_id_generator_error(self):
        platform = Platform('Bayesian')
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
            platform = Platform('Bayesian')
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
        platform = Platform('Bayesian')

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
