import os
from functools import partial

import pytest

from idmtools.assets import AssetCollection, Asset
from idmtools_models.python import PythonExperiment, PythonSimulation
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
import io
import unittest.mock


def param_update(simulation, param, value):
    return simulation.set_parameter(param, value)


setA = partial(param_update, param="a")
setB = partial(param_update, param="b")
setC = partial(param_update, param="c")


class setParam:
    def __init__(self, param):
        self.param = param

    def __call__(self, simulation, value):
        return param_update(simulation, self.param, value)


class TestPythonSimulation(ITestWithPersistence):
    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)

    def test_retrieve_extra_libraries(self):
        ps = PythonExperiment(name=self.case_name, model_path=os.path.join(COMMON_INPUT_PATH, "python", "model.py"))
        self.assertTrue("numpy" in ps.retrieve_python_dependencies()[0])

    def test_add_class_tag(self):
        ps = PythonExperiment(name=self.case_name, model_path=os.path.join(COMMON_INPUT_PATH, "python", "model.py"))
        # The tag for type is added at runtime during the pre_creation event
        ps.pre_creation()
        self.assertEqual(ps.tags.get('type'), "idmtools_models.python.python_experiment.PythonExperiment")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_envelope(self, mock_stdout):
        import json
        # No envelope
        p = PythonSimulation(parameters={"a": 1})

        self.assertEqual(p.parameters, {"a": 1})
        p.gather_assets()
        self.assertEqual(p.assets.assets[0].bytes, str.encode(json.dumps({"a": 1})))

        # Envelope
        p = PythonSimulation(parameters={"a": 1}, envelope="config")

        self.assertEqual(p.parameters, {"a": 1})
        p.gather_assets()
        self.assertEqual(p.assets.assets[0].bytes, str.encode(json.dumps({"config": {"a": 1}})))

        # Envelope already set in parameters
        p = PythonSimulation(parameters={"config": {"a": 1}}, envelope="config")
        self.assertEqual(p.parameters, {"a": 1})
        p.gather_assets()
        self.assertEqual(p.assets.assets[0].bytes, str.encode(json.dumps({"config": {"a": 1}})))

        # Envelope already set in parameters but no envelope parameter
        p = PythonSimulation(parameters={"config": {"a": 1}})
        self.assertEqual(p.parameters, {"config": {"a": 1}})
        p.gather_assets()
        self.assertEqual(p.assets.assets[0].bytes, str.encode(json.dumps({"config": {"a": 1}})))

        print(p)  # verify __repr__method in ISumulation
        self.assertIn("<Simulation: " + p.uid + " - Exp_id: None>", mock_stdout.getvalue())

    @pytest.mark.python
    @pytest.mark.assets
    def test_add_assets_to_python_experiment(self):
        ac = AssetCollection()
        a = Asset(relative_path="MyExternalLibrary",
                  absolute_path=os.path.join(COMMON_INPUT_PATH, "python", "Assets", "MyExternalLibrary",
                                             "functions.py"))
        ac.add_asset(a)
        pe = PythonExperiment(name=self.case_name, model_path=os.path.join(COMMON_INPUT_PATH, "python", "model.py"),
                              assets=ac)
        pe.pre_creation()
        assets_to_find = [
            Asset(relative_path='MyExternalLibrary', filename="functions.py"),
            Asset(relative_path='', filename="model.py")
        ]
        assets_in_pythonexperiment = []
        for asset in pe.assets:
            assets_in_pythonexperiment.append(Asset(relative_path=asset.relative_path, filename=asset.filename))

        self.assertSetEqual(set(assets_in_pythonexperiment), set(assets_to_find))

    @pytest.mark.python
    def test_add_assets_after_python_experiment_created(self):
        ac = AssetCollection()
        a = Asset(relative_path="MyExternalLibrary",
                  absolute_path=os.path.join(COMMON_INPUT_PATH, "python", "Assets", "MyExternalLibrary",
                                             "functions.py"))
        ac.add_asset(a)
        pe = PythonExperiment(name=self.case_name, model_path=os.path.join(COMMON_INPUT_PATH, "python", "model.py"))
        pe.add_assets(ac)
        pe.pre_creation()
        assets_to_find = [
            Asset(relative_path='MyExternalLibrary', filename="functions.py"),
            Asset(relative_path='', filename="model.py")
        ]
        assets_in_pythonexperiment = []
        for asset in pe.assets:
            assets_in_pythonexperiment.append(Asset(relative_path=asset.relative_path, filename=asset.filename))

        self.assertSetEqual(set(assets_in_pythonexperiment), set(assets_to_find))


if __name__ == '__main__':
    unittest.main()
