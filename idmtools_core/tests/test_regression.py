import os
import unittest

from idmtools.assets import AssetCollection
from tests import INPUT_PATH
from tests.utils.ITestWithPersistence import ITestWithPersistence
from idmtools_models.python import PythonExperiment


class TestPersistenceServices(ITestWithPersistence):

    def test_fix_107(self):
        # https://github.com/InstituteforDiseaseModeling/idmtools/issues/107
        assets_path = os.path.join(INPUT_PATH, "regression", "107", "Assets")
        pe = PythonExperiment(name="Test",
                              model_path=os.path.join(assets_path, "model.py"),
                              assets=AssetCollection.from_directory(assets_path))
        pe.gather_assets()


if __name__ == '__main__':
    unittest.main()
