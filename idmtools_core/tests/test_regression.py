import os
import unittest

from idmtools.assets import AssetCollection
from idmtools.builders import StandAloneSimulationsBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.itask import task_to_experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.test_task import TestTask


class TestPersistenceServices(ITestWithPersistence):
    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)

    def test_fix_107(self):
        # https://github.com/InstituteforDiseaseModeling/idmtools/issues/107
        assets_path = os.path.join(COMMON_INPUT_PATH, "regression", "107", "Assets")
        sp = os.path.join(assets_path, "model.py")
        pe = Experiment.from_task(name=self.case_name, task=JSONConfiguredPythonTask(script_path=sp),
                                  assets=AssetCollection.from_directory(assets_path))
        pe.gather_assets()
        self.assertEqual(len(pe.assets.assets), 2)
        expected_files = ['model.py', '__init__.py']
        actual_files = [asset.filename for asset in pe.assets.assets]
        self.assertEqual(actual_files.sort(), expected_files.sort())

    def test_fix_114(self):
        # https://github.com/InstituteforDiseaseModeling/idmtools/issues/114
        assets_path = os.path.join(COMMON_INPUT_PATH, "regression", "107", "Assets")
        sp = os.path.join(assets_path, "model.py")
        s = Simulation.from_task(JSONConfiguredPythonTask(script_path=sp, parameters={"a": 1}))
        ts = TemplatedSimulations(base_task=JSONConfiguredPythonTask(script_path=sp, parameters={"a": 1}))
        self.assertEqual(ts.base_simulation, s)

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

    def test_fix_138(self):
        # https://github.com/InstituteforDiseaseModeling/idmtools/issues/138
        ts = TemplatedSimulations(base_task=TestTask())
        e = Experiment(simulations=ts)
        # Set a parameter in the base simulation
        ts.base_simulation.task.set_parameter("test", 0)
        self.assertEqual(ts.base_simulation.task.parameters["test"], 0)

        # Create a standalone simulation
        s = ts.new_simulation()
        s.task.set_parameter("test", 10)
        self.assertEqual(s.task.parameters["test"], 10)

        # Create a builder and add this simulation
        b = StandAloneSimulationsBuilder()
        b.add_simulation(s)
        ts.add_builder(b)

        # Make sure the simulation in the builder is correct
        self.assertEqual(b.simulations[0].task.parameters["test"], 10)
        self.assertEqual(b.simulations[0], s)

        # Run the experiment
        p = Platform("Test")
        p.run_items(e)

        # Make sure the base simulation was left untouched
        self.assertEqual(ts.base_simulation.task.parameters["test"], 0)
        self.assertEqual(s.task.parameters["test"], 10)

        # Ensure that we actually ran with the correct parameter
        print(p._simulations.simulations[e.uid])
        self.assertEqual(p._simulations.simulations[e.uid][0].task.parameters["test"], 10, "Parameter in platform")
        p.cleanup()

    def test_fix_170(self):
        # https://github.com/InstituteforDiseaseModeling/idmtools/issues/170
        e = Experiment.from_task(TestTask(), gather_common_assets_from_task=True)
        e.tags = {"test": 1}
        e.pre_creation()
        self.assertEqual(e.tags.get("task_type"), "idmtools_test.utils.test_task.TestTask")
        self.assertEqual(e.tags.get("test"), 1)


if __name__ == '__main__':
    unittest.main()
