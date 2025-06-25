import allure
import os
import unittest.mock

import pytest

from idmtools.core.platform_factory import Platform
from idmtools.entities.simulation import Simulation
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence

from idmtools_test.utils.test_task import TestTask


@pytest.mark.smoke
@allure.story("Python")
@allure.suite("idmtools_core")
class TestPythonSimulation(ITestWithPersistence):
    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)

    def test_add_task_tag(self):
        test_platform = Platform("Test")
        base_task = TestTask()
        sim = Simulation.from_task(base_task)
        # The tag for type is added at runtime during the pre_creation event
        sim.pre_creation(test_platform)
        self.assertIsNone(sim.tags.get('task_type'))


if __name__ == '__main__':
    unittest.main()
