import os
import unittest

from idmtools.assets import AssetCollection
from idmtools.builders import SimulationBuilder, StandAloneSimulationsBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools.managers import ExperimentManager
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_models.python import PythonExperiment, PythonSimulation
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.test_task import TestTask


class TestPersistenceServices(ITestWithPersistence):

    def test_fix_107(self):
        # https://github.com/InstituteforDiseaseModeling/idmtools/issues/107
        assets_path = os.path.join(COMMON_INPUT_PATH, "regression", "107", "Assets")
        pe = PythonExperiment(name="Test",
                              model_path=os.path.join(assets_path, "model.py"),
                              assets=AssetCollection.from_directory(assets_path))
        pe.gather_assets()
        self.assertEqual(len(pe.assets.assets), 2)
        expected_files = ['model.py', '__init__.py']
        actual_files = [asset.filename for asset in pe.assets.assets]
        self.assertEqual(actual_files.sort(), expected_files.sort())

    def test_fix_114(self):
        # https://github.com/InstituteforDiseaseModeling/idmtools/issues/114
        assets_path = os.path.join(COMMON_INPUT_PATH, "regression", "107", "Assets")
        s = PythonSimulation(parameters={"a": 1})
        e = PythonExperiment(name="Test",
                             model_path=os.path.join(assets_path, "model.py"),
                             base_simulation=s)
        self.assertEqual(e.base_simulation, s)

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

    def test_fix_142(self):
        # https://github.com/InstituteforDiseaseModeling/idmtools/issues/142
        ts = TemplatedSimulations(base_task=TestTask())
        b = SimulationBuilder()
        b.add_sweep_definition(lambda simulation, v: {"p": v}, range(500))
        ts.builder = b

        counter = 0
        for item in ts:
            self.assertEqual(len(batch), 100)
            counter += 1
        self.assertEqual(counter, 5)

        b = SimulationBuilder()
        b.add_sweep_definition(lambda simulation, v: {"p": v}, range(500))
        ts.builder = b
        counter = 0
        for batch in ts.batch_simulations(200):
            self.assertTrue(len(batch) in (100, 200))
            counter += 1
        self.assertEqual(counter, 3)

    def test_fix_138(self):
        # https://github.com/InstituteforDiseaseModeling/idmtools/issues/138
        e = TstExperiment(name="test")
        p = Platform('Test')
        e.platform = p
        # Set a parameter in the base simulation
        e.base_simulation.set_parameter("test", 0)
        self.assertEqual(e.base_simulation.parameters["test"], 0)

        # Create a standalone simulation
        s = e.simulation()
        s.set_parameter("test", 10)
        self.assertEqual(s.parameters["test"], 10)

        # Create a builder and add this simulation
        b = StandAloneSimulationsBuilder()
        b.add_simulation(s)
        e.builder = b

        # Make sure the simulation in the builder is correct
        self.assertEqual(b.simulations[0].parameters["test"], 10)
        self.assertEqual(b.simulations[0], s)

        # Run the experiment

        em = ExperimentManager(e, platform=p)
        em.run()

        # Make sure the base simulation was left untouched
        self.assertEqual(e.base_simulation.parameters["test"], 0)
        self.assertEqual(s.parameters["test"], 10)

        # Ensure that we actually ran with the correct parameter
        print(p._simulations.simulations[em.experiment.uid])
        self.assertEqual(p._simulations.simulations[em.experiment.uid][0].parameters["test"], 10, "Parameter in platform")
        p.cleanup()

    def test_fix_170(self):
        # https://github.com/InstituteforDiseaseModeling/idmtools/issues/170
        e = TstExperiment("Experiment")
        e.tags = {"test": 1}
        e.pre_creation()
        self.assertEqual(e.tags.get("type"), "idmtools_test.utils.tst_experiment.TstExperiment")
        self.assertEqual(e.tags.get("test"), 1)


if __name__ == '__main__':
    unittest.main()
