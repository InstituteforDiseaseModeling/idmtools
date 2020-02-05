import os
import sys
import unittest
import json
import pytest

from idmtools.assets.FileList import FileList
from idmtools.core.platform_factory import Platform
from idmtools.managers.work_item_manager import WorkItemManager
from idmtools.ssmt.ssmt_work_item import SSMTWorkItem
from COMPS.Data.WorkItem import WorkItem
from functools import partial
from idmtools.builders import ExperimentBuilder
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_models.python.python_experiment import PythonExperiment
from idmtools_test.utils.utils import del_file
from idmtools_models.python.python_task import PythonTask, JSONConfiguredPythonTask
from idmtools_test import COMMON_INPUT_PATH
from examples import EXAMPLES_PATH


class TestSsmtWorkItemPythonExp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # create a simple python experiment to analyze
        cls.exp_name = "idmtools hello_world python model"
        cls.platform = Platform('COMPS2')
        model_path = os.path.join(COMMON_INPUT_PATH, "python", "hello_world.py")
        experiment = PythonExperiment(name=cls.exp_name,
                                      model_path=model_path)
        experiment.tags["tag1"] = 1
        experiment.base_simulation.set_parameter("c", 0)
        experiment.assets.add_directory(assets_directory=os.path.join(COMMON_INPUT_PATH, "python", "Assets"))

        # Update and set simulation configuration parameters
        def param_update(simulation, param, value):
            return simulation.set_parameter(param, value)

        setA = partial(param_update, param="a")

        # Now that the experiment is created, we can add sweeps to it
        builder = ExperimentBuilder()
        builder.add_sweep_definition(setA, range(10))

        experiment.add_builder(builder)

        em = ExperimentManager(experiment=experiment, platform=cls.platform)
        # The last step is to call run() on the ExperimentManager to run the simulations.
        em.run()

        cls.exp_id = experiment.uid

    def setUp(self):
        print(self._testMethodName)
        self.wi_name = "idmtools SSMTAnalysis Test: AssetCollection Hello 1"
        self.tags = {'idmtools': self._testMethodName, 'WorkItem type': 'Docker'}
        self.platform = Platform('COMPS2')

    def test_ssmtanalysis_python_analysis(self):
        command = "python hello.py"
        python_files = os.path.join(EXAMPLES_PATH, "ssmt", "hello_world", "files")
        user_files = FileList(root=python_files)
        wi = SSMTWorkItem(item_name=self.wi_name, command=command, user_files=user_files, tags=self.tags)
        wim = WorkItemManager(wi, self.platform)
        wim.process(check_status=True)
        self.validate(wi)

    #------------------------------------------
    # validate results from analyzer output against each simulation's insetChart.json
    #------------------------------------------
    def validate(self, wi, output_path=None):
        # get workitem
        self.workitem_id = wi.uid
        wi = WorkItem.get(wi.uid)
        print("workitem id :" + str(wi.id))

        # retriever 'stdout.txt' file from Output tab of workitem and save to local disk
        if output_path is None:
            barr_out = wi.retrieve_output_files(['stdout.txt'])
        else:  # if output has folder, retriever from there
            barr_out = wi.retrieve_output_files([os.path.join(output_path, 'stdout.txt')])
        with open("stdout.txt", 'wb') as file:
            file.write(barr_out[0])

        # asset file exists
        self.assertTrue(os.path.exists('stdout.txt'))

        with open("stdout.txt") as f:
            if 'Hello World...' in f.read():
                result = True
                self.assertEqual(result, True)
