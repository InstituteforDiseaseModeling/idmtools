import os
import unittest
from functools import partial
from typing import Any, Dict

from idmtools.builders import SimulationBuilder
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask


class TestGetFiles(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        job_directory = "DEST"
        cls.platform = Platform("Container", job_directory=job_directory)

        builder = SimulationBuilder()

        # Sweep parameter "a"
        def param_update(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
            return simulation.task.set_parameter(param, value)

        builder.add_sweep_definition(partial(param_update, param="a"), range(3))
        builder.add_sweep_definition(partial(param_update, param="b"), range(5))

        task = JSONConfiguredPythonTask(script_path=os.path.join("inputs", "model3.py"),
                                        envelope="parameters", parameters=(dict(c=0)))
        task.python_path = "python3"
        tags = {"string_tag": "test", "number_tag": 123}
        ts = TemplatedSimulations(base_task=task)
        ts.add_builder(builder)
        experiment = Experiment.from_template(ts, name="test_exp", tags=tags)
        experiment.assets.add_directory(assets_directory=os.path.join("inputs", "Assets"))
        experiment.run(True, platform=cls.platform)
        cls.exp_id = experiment.uid
        cls.experiment = experiment

    def setUp(self) -> None:
        self.case_name = f"output/{self._testMethodName}"
        
    def test_get_files_simulation(self):
        simulation = self.platform.get_item(self.experiment.simulations[0].id, ItemType.SIMULATION, raw=False)
        files = ["config.json", "metadata.json", "output/result.txt"]
        ret_files = self.platform.get_files(simulation, files=files, output=self.case_name)
        self.assertEqual(len(ret_files), 3)
        self._verify_files(ret_files, files)

    def test_get_files_file_simulation(self):
        simulation = self.platform.get_item(self.experiment.simulations[0].id, ItemType.SIMULATION, raw=True)
        files = ["config.json", "metadata.json", "output/result.txt"]
        ret_files = self.platform.get_files(simulation, files=files, output=self.case_name)
        self.assertEqual(len(ret_files), 3)
        self._verify_files(ret_files, files)

    def test_get_files_by_id_simulations(self):
        sim_id = self.platform.get_item(self.experiment.simulations[0].id, ItemType.SIMULATION).id
        files = ["config.json", "metadata.json", "output/result.txt"]
        ret_files = self.platform.get_files_by_id(sim_id,
                                                  item_type=ItemType.SIMULATION, files=files, output=self.case_name)
        self.assertEqual(len(ret_files), 3)
        self._verify_files(ret_files, files)

    def test_get_files_experiment(self):
        experiment = self.platform.get_item(self.experiment.id, ItemType.EXPERIMENT, raw=False)
        files = ["config.json", "metadata.json", "output/result.txt"]
        ret_files = self.platform.get_files(experiment, files=files, output=self.case_name)
        # ret_files is a dictionary with key as sim id and the values as a dict of filename as key and values
        # being binary data from file or a dict.
        # Verify each entry for each entry(sim), make sure every sim returns 3 files
        for sim in experiment.simulations:
            convert_file_path = []
            for key, value in ret_files[sim.id].items():
                convert_file_path.append(key.replace("\\", "/"))
                self.assertIsNotNone(value)
                self.assertTrue(len(value) > 0)
            assert set(convert_file_path) == set(files)


    def _verify_files(self, actual_files, expected_files):
        convert_file_path = []
        for key, value in actual_files.items():
            convert_file_path.append(key.replace("\\", "/"))
            self.assertIsNotNone(value)
            self.assertTrue(len(value) > 0)
        assert set(convert_file_path) == set(expected_files)
