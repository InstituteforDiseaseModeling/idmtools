import copy
import json
import os
import sys
import unittest
from functools import partial
from operator import itemgetter
from typing import Any, Dict

import pytest
from COMPS.Data import Experiment as COMPSExperiment, AssetCollection as COMPSAssetCollection
from COMPS.Data import QueryCriteria
from idmtools import __version__
from idmtools.assets import Asset, AssetCollection
from idmtools.builders import ArmSimulationBuilder, ArmType, SimulationBuilder, StandAloneSimulationsBuilder, SweepArm
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.common_experiments import get_model1_templated_experiment, get_model_py_templated_experiment, \
    wait_on_experiment_and_check_all_sim_status
from idmtools_test.utils.comps import get_asset_collection_id_for_simulation_id, get_asset_collection_by_id
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_platform_comps.utils.python_requirements_ac.requirements_to_asset_collection import \
    RequirementsToAssetCollection

setA = partial(JSONConfiguredPythonTask.set_parameter_sweep_callback, param="a")
setB = partial(JSONConfiguredPythonTask.set_parameter_sweep_callback, param="b")
setC = partial(JSONConfiguredPythonTask.set_parameter_sweep_callback, param="c")


class setParam:
    def __init__(self, param: str):
        self.param = param

    def __call__(self, simulation: Simulation, value) -> Dict[str, any]:
        return JSONConfiguredPythonTask.set_parameter_sweep_callback(simulation, self.param, value)


@pytest.mark.comps
@pytest.mark.python
class TestCOMPSSlurmExperiment(ITestWithPersistence):
    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)
        self.platform = Platform('SLURM', node_group=None)

    @pytest.mark.long
    def test_sweeps_with_partial_comps_in_slurm(self):
        model_path = os.path.join(COMMON_INPUT_PATH, "python", "model1.py")
        e = Experiment(name=self.case_name,
                       simulations=TemplatedSimulations(
                           base_task=JSONConfiguredPythonTask(python_path="python3", script_path=model_path)
                       ))
        e.tags = {"string_tag": "test", "number_tag": 123, "KeyOnly": None}
        builder = SimulationBuilder()
        # ------------------------------------------------------
        # Sweeping parameters:
        # first way to sweep parameter 'a' is to use param_update function
        builder.add_sweep_definition(setA, range(0, 2))

        # second way to sweep parameter 'b' is to use class setParam which basiclly doing same thing as param_update
        # method
        builder.add_sweep_definition(setParam("b"), [i * i for i in range(1, 4, 2)])
        # ------------------------------------------------------

        e.simulations.add_builder(builder)

        wait_on_experiment_and_check_all_sim_status(self, e, self.platform)
        experiment = COMPSExperiment.get(e.uid)
        print(experiment.id)
        exp_id = experiment.id
        # exp_id = "a727e802-d88b-e911-a2bb-f0921c167866"

        # validation each simulation output to compare output/config.json is equal to config.json
        self.validate_output(exp_id, 4)

        expected_tags = [{'a': '0', 'b': '1'}, {'a': '0', 'b': '9'}, {'a': '1', 'b': '1'}, {'a': '1', 'b': '9'}]
        self.validate_sim_tags(exp_id, expected_tags)

        # validate experiment tags
        actual_exp_tags = experiment.get(experiment.id, QueryCriteria().select_children('tags')).tags
        expected_exp_tags = {'idmtools': __version__, 'number_tag': '123', 'string_tag': 'test',
                             'KeyOnly': '',
                             'task_type': 'idmtools_models.python.json_python_task.JSONConfiguredPythonTask'}
        self.assertDictEqual(expected_exp_tags, actual_exp_tags)
        self.assertDictEqual(expected_exp_tags, actual_exp_tags)
