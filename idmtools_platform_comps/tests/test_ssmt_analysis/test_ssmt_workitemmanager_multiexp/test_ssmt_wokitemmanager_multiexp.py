from COMPS.Data import Experiment
import unittest
import json
import pytest

from idmtools.assets.file_list import FileList
from idmtools.core.platform_factory import Platform
from idmtools.managers.work_item_manager import WorkItemManager
from idmtools.ssmt.idm_work_item import SSMTWorkItem
import os
from COMPS.Data.WorkItem import WorkItem

from idmtools_test.utils.utils import del_file


class TestSsmtWorkItemEmodMultiExp(unittest.TestCase):

    def setUp(self):
        print(self._testMethodName)
        self.wi_name = "SSMT WorkItemManager Test w Multi Exp"
        self.tags = {'idmtools': self._testMethodName, 'WorkItem type': 'Docker'}

    #------------------------------------------
    # test load all required files to docker's current dir with user_files
    # then run analyzer in docker
    #------------------------------------------
    @pytest.mark.skip
    #TODO: this won't work until a docker image with idmtools is deployed to the comps ssmt server
    def test_ssmt_workitemmanager_multiexp(self):
        command = "python run_PopulationAnalyzer.py"

        # upload 2 files to docker's current folder as linked file
        user_files = FileList(root='.', files_in_root=['PopulationAnalyzer.py', 'run_ssmt_analysis.py'])

        platform = Platform('COMPS2')
        wi = SSMTWorkItem(item_name=self.wi_name, command=command, user_files=user_files,
                          related_experiments=["a585c439-b37d-e911-a2bb-f0921c167866",
                                               "7afc5160-e086-e911-a2bb-f0921c167866"])
        wim = WorkItemManager(wi, platform)
        wim.process(check_status=True)

        self.workitem_id = wi.uid
        wi = WorkItem.get(self.workitem_id)

        self.validate(wi)

    #------------------------------------------
    # validate results from analyzer output against each simulation's insetChart.json
    #------------------------------------------
    def validate(self, wi, output_path=None):
        # # get workitem
        self.workitem_id = wi.id
        wi = WorkItem.get(self.workitem_id)
        print("workitem id :" + str(wi.id))

        # delete results.json file first before same a new one
        del_file("results.json")
        # retrieve 'results.json' file from Output tab of workitem and save to local disk
        if output_path is None:
            barr_out = wi.retrieve_output_files(['results.json'])
        else:  # if output has folder, retriever from there
            barr_out = wi.retrieve_output_files([os.path.join(output_path, 'results.json')])
        with open("results.json", 'wb') as file:
            file.write(barr_out[0])

        # asset file exists
        self.assertTrue(os.path.exists('results.json'))

        # Compare values in results.json to each simulation's insetChart.json's Statistical Population
        with open('results.json') as json_file:
            data = json.load(json_file)

            for simulation in Experiment.get(self.exp_id).get_simulations():
                # read insetChart.json file from each simulation
                insetchartFileString = simulation.retrieve_output_files(paths=['output/InsetChart.json'])

                #convert insetchart string to dictionary
                insetchartDict = json.loads(insetchartFileString[0].decode('utf-8'))

                # We only need retriever 'Statistical Population' from output
                statistical_population = insetchartDict['Channels']['Statistical Population']['Data']

                # validate workitem's results.json have same value as in insetChart for each simulation
                self.assertEqual(statistical_population, data[str(simulation.id)])
