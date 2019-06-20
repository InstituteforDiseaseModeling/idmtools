import os
import unittest

from idmtools.assets import AssetCollection
from idmtools.builders import ExperimentBuilder
from tests import INPUT_PATH
from tests.utils.ITestWithPersistence import ITestWithPersistence
from idmtools_models.python import PythonExperiment, PythonSimulation
from tests.utils.TestExperiment import TestExperiment


class TestPersistenceServices(ITestWithPersistence):

    def test_fix_107(self):
        # https://github.com/InstituteforDiseaseModeling/idmtools/issues/107
        assets_path = os.path.join(INPUT_PATH, "regression", "107", "Assets")
        pe = PythonExperiment(name="Test",
                              model_path=os.path.join(assets_path, "model.py"),
                              assets=AssetCollection.from_directory(assets_path))
        pe.gather_assets()

    def test_fix_114(self):
        # https://github.com/InstituteforDiseaseModeling/idmtools/issues/114
        assets_path = os.path.join(INPUT_PATH, "regression", "107", "Assets")
        s = PythonSimulation(parameters={"a": 1})
        e = PythonExperiment(name="Test",
                             model_path=os.path.join(assets_path, "model.py"),
                             base_simulation=s)
        self.assertEqual(e.base_simulation, s)

    def test_fix_125(self):
        # https://github.com/InstituteforDiseaseModeling/idmtools/issues/125
        ac = AssetCollection()
        ac.add_directory(assets_directory=os.path.join(INPUT_PATH, "regression", "125", "Assets"),
                         relative_path="MyExternalLibrary")
        self.assertTrue(all([a.relative_path == "MyExternalLibrary" for a in ac]))

        ac = AssetCollection()
        ac.add_directory(assets_directory=os.path.join(INPUT_PATH, "regression", "125", "Assets2"),
                         relative_path="MyExternalLibrary")
        self.assertTrue(all([a.relative_path.startswith("MyExternalLibrary") for a in ac]))

    def test_fix_142(self):
        # https://github.com/InstituteforDiseaseModeling/idmtools/issues/142
        e = TestExperiment(name="test")
        b = ExperimentBuilder()
        b.add_sweep_definition(lambda simulation, v: {"p": v}, range(500))
        e.builder = b

        counter = 0
        for batch in e.batch_simulations(100):
            self.assertEqual(len(batch), 100)
            counter += 1
        self.assertEqual(counter, 5)

        b = ExperimentBuilder()
        b.add_sweep_definition(lambda simulation, v: {"p": v}, range(500))
        e.builder = b
        counter = 0
        for batch in e.batch_simulations(200):
            self.assertTrue(len(batch) in (100, 200))
            counter += 1
        self.assertEqual(counter, 3)


if __name__ == '__main__':
    unittest.main()
