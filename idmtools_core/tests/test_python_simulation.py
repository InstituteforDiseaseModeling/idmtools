import allure
import io
import os
import unittest.mock
from functools import partial

import pytest

from idmtools.assets import AssetCollection, Asset
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools_models.json_configured_task import JSONConfiguredTask
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence

setA = partial(JSONConfiguredTask.set_parameter_sweep_callback, param="a")
setB = partial(JSONConfiguredTask.set_parameter_sweep_callback, param="b")
setC = partial(JSONConfiguredTask.set_parameter_sweep_callback, param="c")


class setParam:
    def __init__(self, param):
        self.param = param

    def __call__(self, simulation, value):
        return JSONConfiguredTask.set_parameter_sweep_callback(simulation, self.param, value)


@pytest.mark.smoke
@allure.story("JSONConfiguredTask")
@allure.story("Python")
@allure.suite("idmtools_core")
class TestPythonSimulation(ITestWithPersistence):
    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)

    def test_add_task_tag(self):
        ps = Simulation(task=JSONConfiguredTask(parameters={"a": 1}, envelope="config", command="ls"))
        # The tag for type is added at runtime during the pre_creation event
        ps.pre_creation(None)
        self.assertEqual(ps.tags.get('task_type'), 'idmtools_models.json_configured_task.JSONConfiguredTask')

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_envelope(self, mock_stdout):
        import json
        # No envelope
        p = JSONConfiguredTask(parameters={"a": 1})

        self.assertEqual(p.parameters, {"a": 1})
        p.gather_transient_assets()
        self.assertEqual(p.transient_assets.assets[0].bytes, str.encode(json.dumps({"a": 1})))

        # Envelope
        p = JSONConfiguredTask(parameters={"a": 1}, envelope="config")

        self.assertEqual(p.parameters, {"a": 1})
        p.gather_transient_assets()
        self.assertEqual(p.transient_assets.assets[0].bytes, str.encode(json.dumps({"config": {"a": 1}})))

        # Envelope already set in parameters
        p = JSONConfiguredTask(parameters={"config": {"a": 1}}, envelope="config")
        self.assertEqual(p.parameters, {"a": 1})
        p.gather_transient_assets()
        self.assertEqual(p.transient_assets.assets[0].bytes, str.encode(json.dumps({"config": {"a": 1}})))

        # Envelope already set in parameters but no envelope parameter
        p = JSONConfiguredTask(parameters={"config": {"a": 1}})
        self.assertEqual(p.parameters, {"config": {"a": 1}})
        p.gather_transient_assets()
        self.assertEqual(p.transient_assets.assets[0].bytes, str.encode(json.dumps({"config": {"a": 1}})))

        print(p)  # verify __repr__method in ITask
        self.assertIn("JSONConfiguredTask config", mock_stdout.getvalue())

    @pytest.mark.python
    @pytest.mark.assets
    def test_add_assets_to_python_experiment(self):
        ac = self.create_functions_asset_collection()
        sp = os.path.join(COMMON_INPUT_PATH, "python", "model.py")
        pe = Experiment.from_task(name=self.case_name, task=JSONConfiguredPythonTask(script_path=sp), assets=ac)
        pe.pre_creation(None)
        assets_to_find = [
            Asset(relative_path='MyExternalLibrary', filename="functions.py",
                  absolute_path=os.path.join(COMMON_INPUT_PATH, "python", "Assets", "MyExternalLibrary", "functions.py")),
            Asset(relative_path='', filename="model.py", absolute_path=os.path.join(COMMON_INPUT_PATH, "python", "model.py"))
        ]
        assets_in_pythonexperiment = []
        for asset in pe.assets:
            assets_in_pythonexperiment.append(Asset(relative_path=asset.relative_path, filename=asset.filename, absolute_path=asset.absolute_path))

        self.assertSetEqual(set(assets_in_pythonexperiment), set(assets_to_find))

    def create_functions_asset_collection(self):
        ac = AssetCollection()
        a = Asset(relative_path="MyExternalLibrary",
                  absolute_path=os.path.join(COMMON_INPUT_PATH, "python", "Assets", "MyExternalLibrary",
                                             "functions.py"))
        ac.add_asset(a)
        return ac

    @pytest.mark.python
    def test_add_assets_after_python_experiment_created(self):
        ac = self.create_functions_asset_collection()
        sp = os.path.join(COMMON_INPUT_PATH, "python", "model.py")
        pe = Experiment.from_task(name=self.case_name, task=JSONConfiguredPythonTask(script_path=sp))
        pe.add_assets(ac)
        pe.pre_creation(None)
        assets_to_find = [
            Asset(relative_path='MyExternalLibrary', filename="functions.py",
                  absolute_path=os.path.join(COMMON_INPUT_PATH, "python", "Assets", "MyExternalLibrary", "functions.py")),
            Asset(relative_path='', filename="model.py", absolute_path=os.path.join(COMMON_INPUT_PATH, "python", "model.py"))
        ]
        assets_in_pythonexperiment = []
        for asset in pe.assets:
            assets_in_pythonexperiment.append(Asset(relative_path=asset.relative_path, filename=asset.filename, absolute_path=asset.absolute_path))

        self.assertSetEqual(set(assets_in_pythonexperiment), set(assets_to_find))


if __name__ == '__main__':
    unittest.main()
