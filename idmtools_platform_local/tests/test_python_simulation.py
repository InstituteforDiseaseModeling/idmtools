import os
from functools import partial
from operator import itemgetter

import pytest

from idmtools.assets import AssetCollection
from idmtools.builders import SimulationBuilder
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.common_experiments import wait_on_experiment_and_check_all_sim_status
from idmtools_test.utils.confg_local_runner_test import get_test_local_env_overrides
from idmtools_test.utils.decorators import restart_local_platform
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence

param_a = partial(JSONConfiguredPythonTask.set_parameter_sweep_callback, param="a")


@pytest.mark.docker
@pytest.mark.python
class TestPythonSimulation(ITestWithPersistence):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName

    @pytest.mark.long
    @pytest.mark.timeout(90)
    @restart_local_platform(silent=True, **get_test_local_env_overrides())
    def test_direct_sweep_one_parameter_local(self):
        platform = Platform('Local')
        name = self.case_name
        basetask = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"))

        builder = SimulationBuilder()
        # Sweep parameter "a"
        builder.add_sweep_definition(param_a, range(0, 5))
        e = Experiment.from_template(template=TemplatedSimulations(base_task=basetask, builders={builder}), name=name)

        wait_on_experiment_and_check_all_sim_status(self, e, platform)

        # validation
        self.assertEqual(e.name, name)
        self.assertEqual(e.simulation_count, 5)
        self.assertIsNotNone(e.uid)

        # validate tags
        tags = []
        for simulation in e.simulations:
            self.assertEqual(simulation.experiment.uid, e.uid)
            tags.append(simulation.tags)
        expected_tags = [{'a': 0}, {'a': 1}, {'a': 2}, {'a': 3}, {'a': 4}]
        sorted_tags = sorted(tags, key=itemgetter('a'))
        sorted_expected_tags = sorted(expected_tags, key=itemgetter('a'))
        self.assertEqual(sorted_tags, sorted_expected_tags)

    @pytest.mark.long
    @pytest.mark.timeout(90)
    @restart_local_platform(silent=True, **get_test_local_env_overrides())
    def test_add_prefixed_relative_path_to_assets_local(self):
        # platform = Platform('COMPS2', endpoint="https://comps2.idmod.org", environment="Bayesian")
        platform = Platform('Local')
        model_path = os.path.join(COMMON_INPUT_PATH, "python", "model.py")
        ac = AssetCollection()
        assets_path = os.path.join(COMMON_INPUT_PATH, "python", "Assets", "MyExternalLibrary")
        ac.add_directory(assets_directory=assets_path, relative_path="MyExternalLibrary")
        # assets_path = os.path.join(COMMON_INPUT_PATH, "python", "Assets")
        # ac.add_directory(assets_directory=assets_path)
        builder = SimulationBuilder()
        # Sweep parameter "a"
        builder.add_sweep_definition(param_a, range(0, 2))
        task = JSONConfiguredPythonTask(script_path=model_path, envelope="parameters", parameters=dict(b=10))
        pe = Experiment.from_template(template=TemplatedSimulations(base_task=task, builders={builder}),
                                      name=self.case_name, assets=ac)
        pe.tags = {"string_tag": "test", "number_tag": 123,
                   "task_type": "idmtools_models.python.json_python_task.JSONConfiguredPythonTask"}

        wait_on_experiment_and_check_all_sim_status(self, pe, platform)

        with self.subTest('test_retrieve_experiment_restore_sims'):
            # test we can fetch the experiment as well
            oe = platform.get_item(pe.uid, ItemType.EXPERIMENT)
            oe.refresh_simulations()
            self.assertEqual(pe.uid, oe.uid)
            self.assertEqual(len(pe.simulations), len(oe.simulations))
            sim_ids_pe = set([s.uid for s in pe.simulations])
            sim_ids_oe = set([s.uid for s in oe.simulations])
            # get difference. There should be none so we should get an empty array
            self.assertEqual(len(sim_ids_oe.difference(sim_ids_pe)), 0)
            # intersection should be 100% of array
            self.assertEqual(len(sim_ids_oe.intersection(sim_ids_pe)), len(sim_ids_oe))

            self.assertDictEqual(oe.tags, pe.tags)

            # test simulations have all tags
            for sim in pe.simulations:
                # get our sim
                osim = [o for o in oe.simulations if o.uid == sim.uid][0]
                self.assertDictEqual(sim.tags, osim.tags)
                self.assertEqual(sim.succeeded, osim.succeeded)
