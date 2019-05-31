import os
import unittest

from idmtools_models.python.PythonExperiment import PythonExperiment


class TestPythonSimulation(unittest.TestCase):

    def test_retrieve_extra_libraries(self):
        ps = PythonExperiment(name="Test experiment", model_path=os.path.join("inputs", "python", "model.py"))
        self.assertListEqual(ps.retrieve_python_dependencies(), ["numpy==1.16.3"])


if __name__ == '__main__':
    unittest.main()
