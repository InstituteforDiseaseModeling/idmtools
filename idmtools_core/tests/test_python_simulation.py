import os
import unittest

from idmtools_models.python.PythonExperiment import PythonExperiment
from tests import INPUT_PATH


class TestPythonSimulation(unittest.TestCase):

    def test_retrieve_extra_libraries(self):
        ps = PythonExperiment(name="Test experiment", model_path=os.path.join(INPUT_PATH, "python", "model.py"))
        self.assertListEqual(ps.retrieve_python_dependencies(), ["numpy==1.16.3"])


if __name__ == '__main__':
    unittest.main()
