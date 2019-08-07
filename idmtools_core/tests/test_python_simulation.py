import os
import unittest
from functools import partial
from idmtools_models.python import PythonExperiment, PythonSimulation
from idmtools_test.utils.ITestWithPersistence import ITestWithPersistence
from idmtools_test import COMMON_INPUT_PATH


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
        self.assertEqual(ps.tags.get('type'), "idmtools_models.python.PythonExperiment")

    def test_envelope(self):
        import json
        # No envelope
        p = PythonSimulation(parameters={"a": 1})
        self.assertEqual(p.parameters, {"a": 1})
        p.gather_assets()
        self.assertEqual(p.assets.assets[0].content, str.encode(json.dumps({"a": 1})))

        # Envelope
        p = PythonSimulation(parameters={"a": 1}, envelope="config")
        self.assertEqual(p.parameters, {"a": 1})
        p.gather_assets()
        self.assertEqual(p.assets.assets[0].content, str.encode(json.dumps({"config": {"a": 1}})))

        # Envelope already set in parameters
        p = PythonSimulation(parameters={"config": {"a": 1}}, envelope="config")
        self.assertEqual(p.parameters, {"a": 1})
        p.gather_assets()
        self.assertEqual(p.assets.assets[0].content, str.encode(json.dumps({"config": {"a": 1}})))

        # Envelope already set in parameters but no envelope parameter
        p = PythonSimulation(parameters={"config": {"a": 1}})
        self.assertEqual(p.parameters, {"config": {"a": 1}})
        p.gather_assets()
        self.assertEqual(p.assets.assets[0].content, str.encode(json.dumps({"config": {"a": 1}})))


if __name__ == '__main__':
    unittest.main()
