import os

import pytest

from idmtools_model_emod import EMODExperiment
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence


@pytest.mark.comps
class TestEMOD(ITestWithPersistence):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)

    def test_command(self):
        models_dir = os.path.join(COMMON_INPUT_PATH, "fakemodels", "Eradication.exe")
        exp = EMODExperiment(eradication_path=models_dir)
        exp.pre_creation()
        self.assertEqual("Assets/Eradication.exe --config config.json --input-path ./Assets;.", exp.command.cmd)

        models_dir = os.path.join(COMMON_INPUT_PATH, "fakemodels", "Eradication")
        exp = EMODExperiment(eradication_path=models_dir)
        exp.pre_creation()
        self.assertEqual("Assets/Eradication --config config.json --input-path ./Assets;.", exp.command.cmd)

        models_dir = os.path.join(COMMON_INPUT_PATH, "fakemodels", "Eradication-2.11.custom.exe")
        exp = EMODExperiment(eradication_path=models_dir)
        exp.pre_creation()
        self.assertEqual("Assets/Eradication-2.11.custom.exe --config config.json --input-path ./Assets;.",
                         exp.command.cmd)

        models_dir = os.path.join(COMMON_INPUT_PATH, "fakemodels", "AnotherOne")
        exp = EMODExperiment(eradication_path=models_dir)
        exp.pre_creation()
        self.assertEqual("Assets/AnotherOne --config config.json --input-path ./Assets;.", exp.command.cmd)

    def test_legacy_emod(self):
        ext = ".exe" if os.name == "nt" else ""
        models_dir = os.path.join(COMMON_INPUT_PATH, "fakemodels", "Eradication.exe")
        exp = EMODExperiment(eradication_path=models_dir)
        exp.pre_creation()
        self.assertEqual(f"Assets/Eradication{ext} --config config.json --input-path ./Assets;.", exp.command.cmd)

        models_dir = os.path.join(COMMON_INPUT_PATH, "fakemodels", "Eradication.exe")
        exp = EMODExperiment(eradication_path=models_dir, legacy_exe=True)
        exp.pre_creation()
        self.assertEqual(f"Assets/Eradication{ext} --config config.json --input-path ./Assets", exp.command.cmd)
