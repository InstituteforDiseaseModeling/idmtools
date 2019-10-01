import os
import unittest
from functools import partial

import pytest
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence

from idmtools.builders import ExperimentBuilder
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_models.python import PythonExperiment


def param_update(simulation, param, value):
    return simulation.set_parameter(param, value)


setA = partial(param_update, param="a")


@pytest.mark.comps
class TestRetrieval(ITestWithPersistence):
    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)

        self.platform = Platform('COMPS2')
        print(self.platform.uid)
        self.pe = PythonExperiment(name=self.case_name,
                                   model_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"))

        self.pe.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123, "KeyOnly": None}

        self.pe.base_simulation.set_parameter("c", "c-value")
        builder = ExperimentBuilder()
        builder.add_sweep_definition(setA, range(0, 2))

        self.pe.builder = builder

        em = ExperimentManager(experiment=self.pe, platform=self.platform)
        em.run()
        em.wait_till_done()

    def test_retrieve_experiment(self):
        exp = self.platform.get_object(self.pe.uid)
        self.assertEqual(self.pe, exp)

    def test_retrieve_simulation(self):
        sim = self.platform.get_object(self.pe.simulations[0].uid)
        self.assertEqual(sim, self.pe.simulations[0])

    def test_parent(self):
        self.assertEqual(self.pe, self.platform.get_parent(self.pe.simulations[0].uid))
        self.assertIsNone(self.platform.get_parent(self.pe.uid))

    def test_children(self):
        self.assertListEqual(self.pe.simulations, self.platform.get_children(self.pe.uid))
        self.assertIsNone(self.platform.get_children(self.pe.simulations[0].uid))


if __name__ == '__main__':
    unittest.main()
