import os
import pytest
from idmtools.core import EntityStatus
from operator import itemgetter
from idmtools.builders import SimulationBuilder
from idmtools.managers import ExperimentManager
from idmtools_models.python import PythonExperiment
from idmtools.core.platform_factory import Platform
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence

@pytest.mark.skip("Fix test later")
class TestPythonSimulation(ITestWithPersistence):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName

    def test_direct_sweep_one_parameter_local(self):

        platform = Platform('SlurmStage')

        # CreateSimulationTask.broker =

        name = self.case_name
        pe = PythonExperiment(name=self.case_name, model_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"))

        pe.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}

        def param_a_update(simulation, value):
            simulation.set_parameter("a", value)
            return {"a": value}

        builder = SimulationBuilder()
        # Sweep parameter "a"
        builder.add_sweep_definition(param_a_update, range(0, 5))
        pe.builder = builder

        em = ExperimentManager(experiment=pe, platform=platform)
        em.run()
        em.wait_till_done()
        self.assertTrue(all([s.status == EntityStatus.SUCCEEDED for s in pe.simulations]))
        # validation
        self.assertEqual(pe.name, name)
        self.assertEqual(pe.simulation_count, 5)
        self.assertIsNotNone(pe.uid)
        self.assertTrue(all([s.status == EntityStatus.SUCCEEDED for s in pe.simulations]))
        self.assertTrue(pe.succeeded)

        # validate tags
        tags = []
        for simulation in pe.simulations:
            self.assertEqual(simulation.experiment.uid, pe.uid)
            tags.append(simulation.tags)
        expected_tags = [{'a': 0}, {'a': 1}, {'a': 2}, {'a': 3}, {'a': 4}]
        sorted_tags = sorted(tags, key=itemgetter('a'))
        sorted_expected_tags = sorted(expected_tags, key=itemgetter('a'))
        self.assertEqual(sorted_tags, sorted_expected_tags)
