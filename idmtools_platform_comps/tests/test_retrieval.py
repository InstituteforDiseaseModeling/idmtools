import os
import unittest
from functools import partial

import pytest
from COMPS.Data import Experiment as COMPSExperiment, Simulation as COMPSSimulation
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence

from idmtools.builders import ExperimentBuilder
from idmtools.core import ItemType
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

    def test_retrieve_experiment(self):
        exp = self.platform.get_item(self.pe.uid, ItemType.EXPERIMENT)

        # Test attributes
        self.assertEqual(self.pe.uid, exp.uid)
        self.assertEqual(self.pe.name, exp.name)

        # Comps returns tags as string regardless of type
        self.assertEqual({k: str(v or '') for k, v in self.pe.tags.items()}, exp.tags)

        # Test the raw retrieval
        comps_experiment = self.platform.get_item(self.pe.uid, ItemType.EXPERIMENT, raw=True)
        self.assertIsInstance(comps_experiment, COMPSExperiment)
        self.assertEqual(self.pe.uid, comps_experiment.id)
        self.assertEqual(self.pe.name, comps_experiment.name)
        self.assertEqual({k: str(v or '') for k, v in self.pe.tags.items()}, comps_experiment.tags)

        # Test retrieving less columns
        comps_experiment = self.platform.get_item(self.pe.uid, ItemType.EXPERIMENT, raw=True, children=[], columns=["id"])
        self.assertIsNone(comps_experiment.name)
        self.assertIsNone(comps_experiment.tags)
        self.assertEqual(self.pe.uid, comps_experiment.id)

    @unittest.skip
    def test_retrieve_simulation(self):
        base = self.pe.simulations[0]
        sim = self.platform.get_object(base.uid, ItemType.SIMULATION)

        # Test attributes
        self.assertEqual(sim.uid, base.uid)
        self.assertEqual(sim.name, base.name)
        self.assertEqual({k: str(v or '') for k, v in base.tags.items()}, sim.tags)

        # Test the raw retrieval
        comps_simulation = self.platform.get_object(base.uid, ItemType.SIMULATION, raw=True)
        self.assertIsInstance(comps_simulation, COMPSSimulation)
        self.assertEqual(base.uid, comps_simulation.id)
        self.assertEqual(base.name, comps_simulation.name)
        self.assertEqual({k: str(v or '') for k, v in base.tags.items()}, comps_simulation.tags)

    def test_parent(self):
        parent_exp = self.platform.get_parent(self.pe.simulations[0].uid, ItemType.SIMULATION)
        self.assertEqual(self.pe.uid, parent_exp.uid)
        self.assertEqual({k: str(v or '') for k, v in self.pe.tags.items()}, parent_exp.tags)
        self.assertIsNone(self.platform.get_parent(self.pe.uid, ItemType.EXPERIMENT))

    def test_children(self):
        children = self.platform.get_children(self.pe.uid, ItemType.EXPERIMENT)
        self.assertEqual(len(self.pe.simulations), len(children))
        for s in self.pe.simulations:
            self.assertIn(s.uid, [s.uid for s in children])
        self.assertIsNone(self.platform.get_children(self.pe.simulations[0].uid, ItemType.SIMULATION))


if __name__ == '__main__':
    unittest.main()
