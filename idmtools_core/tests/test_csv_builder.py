import allure
import os
import numpy as np
from functools import partial

import pytest
from idmtools.builders import CsvExperimentBuilder
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.test_task import TestTask


def param_update(simulation, param, value):
    return simulation.task.set_parameter(param, value)


setA = partial(param_update, param="a")
setB = partial(param_update, param="b")
setC = partial(param_update, param="c")
setD = partial(param_update, param="d")


@pytest.mark.smoke
@allure.story("Sweeps")
@allure.suite("idmtools_core")
class TestCsvBuilder(ITestWithPersistence):

    def setUp(self):
        super().setUp()
        self.builder = CsvExperimentBuilder()
        self.base_path = os.path.abspath(os.path.join(COMMON_INPUT_PATH, "builder"))

    def tearDown(self):
        super().tearDown()

    def test_simple_csv(self):
        file_path = os.path.join(self.base_path, 'sweeps.csv')
        func_map = {'a': setA, 'b': setB, 'c': setC, 'd': setD}
        type_map = {'a': np.int64, 'b': np.int64, 'c': np.int64, 'd': np.int64}
        self.builder.add_sweeps_from_file(file_path, func_map, type_map)
        self.assertEqual(self.builder.count, 5)

        import pandas as pd

        data = pd.read_csv(file_path).replace({np.nan: None})
        # Convert the DataFrame to a Dictionary
        data_dict = data.to_dict(orient='records')
        expected_values = []
        for d in data_dict:
            expected_values.append({k: int(v) for k, v in d.items() if v is not None})

        templated_sim = TemplatedSimulations(base_task=TestTask())
        templated_sim.builder = self.builder

        simulations = list(templated_sim)

        # Test if we have correct number of simulations
        self.assertEqual(len(simulations), 5)
        for i, simulation in enumerate(simulations):
            self.assertEqual(simulation.task.parameters, expected_values[i])

