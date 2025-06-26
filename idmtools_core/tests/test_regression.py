import allure
import os
import unittest

import pytest
from idmtools.assets import AssetCollection

from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.test_task import TestTask


@pytest.mark.smoke
@allure.story("regression")
@allure.suite("idmtools_core")
class TestPersistenceServices(ITestWithPersistence):
    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)

    @allure.issue(107, "LocalPlatform does not detect duplicate files in AssetCollectionFile for pythonExperiment")
    def test_fix_107(self):
        # https://github.com/InstituteforDiseaseModeling/idmtools/issues/107
        assets_path = os.path.join(COMMON_INPUT_PATH, "regression", "107", "Assets")
        base_task = TestTask()
        pe = Experiment.from_task(name=self.case_name, task=base_task,
                                  assets=AssetCollection.from_directory(assets_path))
        pe.gather_assets()
        self.assertEqual(len(pe.assets.assets), 2)
        expected_files = ['model.py', '__init__.py']
        actual_files = [asset.filename for asset in pe.assets.assets]
        self.assertEqual(actual_files.sort(), expected_files.sort())

    @allure.issue(114, "It should be possible to set `base_simulation` in the `PythonExperiment` constructor")
    def test_fix_114(self):
        # https://github.com/InstituteforDiseaseModeling/idmtools/issues/114
        assets_path = os.path.join(COMMON_INPUT_PATH, "regression", "107", "Assets")
        base_task = TestTask()
        s = Simulation.from_task(task=base_task)
        ts = TemplatedSimulations(base_task=base_task)
        self.assertEqual(ts.base_simulation, s)

    @allure.issue(125, "relative_path for AssetCollection does not work")
    def test_fix_125(self):
        # https://github.com/InstituteforDiseaseModeling/idmtools/issues/125
        ac = AssetCollection()
        ac.add_directory(assets_directory=os.path.join(COMMON_INPUT_PATH, "regression", "125", "Assets"),
                         relative_path="MyExternalLibrary")
        self.assertTrue(all([a.relative_path == "MyExternalLibrary" for a in ac]))

        ac = AssetCollection()
        ac.add_directory(assets_directory=os.path.join(COMMON_INPUT_PATH, "regression", "125", "Assets2"),
                         relative_path="MyExternalLibrary")
        self.assertTrue(all([a.relative_path.startswith("MyExternalLibrary") for a in ac]))

    @allure.issue(170, "tag 'type: idmtools_models.python.PythonExperiment' can be missing for same test")
    def test_fix_170(self):
        # https://github.com/InstituteforDiseaseModeling/idmtools/issues/170
        e = Experiment.from_task(TestTask(), gather_common_assets_from_task=True)
        e.tags = {"test": 1}
        e.pre_creation(None)
        self.assertEqual(e.tags.get("test"), 1)


if __name__ == '__main__':
    unittest.main()
