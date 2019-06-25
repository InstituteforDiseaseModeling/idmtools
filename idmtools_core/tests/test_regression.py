import os
import unittest

from idmtools.assets import AssetCollection
from idmtools.builders import ExperimentBuilder, StandAloneSimulationsBuilder
from idmtools.managers import ExperimentManager
from tests import INPUT_PATH
from tests.utils.ITestWithPersistence import ITestWithPersistence
from idmtools_models.python import PythonExperiment, PythonSimulation
from tests.utils.TestExperiment import TestExperiment
from tests.utils.TestPlatform import TestPlatform


class TestPersistenceServices(ITestWithPersistence):

    def test_fix_107(self):
        # https://github.com/InstituteforDiseaseModeling/idmtools/issues/107
        assets_path = os.path.join(INPUT_PATH, "regression", "107", "Assets")
        pe = PythonExperiment(name="Test",
                              model_path=os.path.join(assets_path, "model.py"),
                              assets=AssetCollection.from_directory(assets_path))
        pe.gather_assets()
        self.assertEqual(len(pe.assets.assets), 2)
        self.assertEqual(pe.assets.assets[0].filename, 'model.py')
        self.assertEqual(pe.assets.assets[1].filename, '__init__.py')

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

    def test_fix_138(self):
        # https://github.com/InstituteforDiseaseModeling/idmtools/issues/138
        e = TestExperiment(name="test")
        p = TestPlatform()

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
        em = ExperimentManager(e, p)
        em.run()

        # Make sure the base simulation was left untouched
        self.assertEqual(e.base_simulation.parameters["test"], 0)
        self.assertEqual(s.parameters["test"], 10)

        # Ensure that we actually ran with the correct parameter
        self.assertEqual(p.simulations[em.experiment.uid][0].parameters["test"], 10, "Parameter in platform")


if __name__ == '__main__':
    unittest.main()
