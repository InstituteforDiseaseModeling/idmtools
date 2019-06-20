import os
import unittest

from idmtools.assets import AssetCollection
from tests import INPUT_PATH
from tests.utils.ITestWithPersistence import ITestWithPersistence
from idmtools_models.python import PythonExperiment, PythonSimulation


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
        s = PythonSimulation(parameters={"a":1})
        e = PythonExperiment(name="Test",
                             model_path=os.path.join(assets_path, "model.py"),
                             base_simulation=s)
        self.assertEqual(e.base_simulation, s)

    def test_fix_125(self):
        # https://github.com/InstituteforDiseaseModeling/idmtools/issues/125
        ac = AssetCollection()
        ac.add_directory(assets_directory=os.path.join(INPUT_PATH, "regression", "107", "Assets"),
                         relative_path="MyExternalLibrary")


if __name__ == '__main__':
    unittest.main()
