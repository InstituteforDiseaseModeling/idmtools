import allure
import unittest

import pytest
from idmtools.entities.experiment import Experiment
from idmtools.entities.suite import Suite


@pytest.mark.smoke
@allure.story("Entities")
@allure.suite("idmtools_core")
class TestSuite(unittest.TestCase):

    def setUp(self):
        self.suite = Suite(name="test")
        self.experiment1 = Experiment('t1')
        self.experiment2 = Experiment('t2')

    def test_suite_add_experiment(self):
        self.suite.add_experiment(self.experiment1)
        self.suite.add_experiment(self.experiment2)
        self.assertEqual(len(self.suite.experiments), 2)
        self.assertEqual(self.suite.id, self.experiment1.suite.id)
        self.assertEqual(self.suite.id, self.experiment2.suite.id)

    def test_suite_setter(self):
        self.experiment1.suite = self.suite
        self.experiment2.suite = self.suite
        self.assertEqual(len(self.suite.experiments), 2)
        self.assertEqual(self.suite.id, self.experiment1.suite.id)
        self.assertEqual(self.suite.id, self.experiment2.suite.id)

    def test_suite_complex(self):
        self.experiment1.suite = self.suite
        self.suite.add_experiment(self.experiment2)
        self.assertEqual(len(self.suite.experiments), 2)
        self.assertEqual(self.suite.id, self.experiment1.suite.id)
        self.assertEqual(self.suite.id, self.experiment2.suite.id)
        self.assertEqual(self.suite.id, self.experiment1.parent.id)
        self.assertEqual(self.suite.id, self.experiment2.parent.id)
