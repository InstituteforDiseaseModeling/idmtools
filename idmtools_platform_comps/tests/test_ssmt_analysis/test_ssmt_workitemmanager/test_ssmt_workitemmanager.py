from simtools.Analysis.AnalyzeManager import AnalyzeManager
from COMPS.Data import Experiment
import unittest
import xmlrunner
import os
import json
import sys

import inspect
from idmtools.assets.FileList import FileList
from idmtools.core.platform_factory import Platform
from idmtools.managers.work_item_manager import WorkItemManager
from idmtools.ssmt.ssmt_work_item import SSMTWorkItem
import os
from COMPS.Data import WorkItem

#sys.path.append('..\..\General')
par_par_dir = os.path.normpath(os.path.join('..', os.pardir))
sys.path.append(os.path.join(par_par_dir,'General'))
from utils import del_file


class RunAnalyzeTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.par_par_dir = par_par_dir
        #Comment out if you do not want to generate exp and sims
        # exp = BuildExperiment()
        # exp.build_experiment(exp_name="Experiment for ssmt")
        # cls.exp_id = exp.exp_id

        # Uncomment out if you do not want to regenerate exp and sims
        cls.exp_id = '08fc74a7-b767-e911-a2b8-f0921c167865'  #exp id in comps2

    def setUp(self):
        print(self._testMethodName)
        self.wi_name = "SSMT WorkItemManager Test"
        self.tags = {'idmtools': self._testMethodName, 'WorkItem type': 'Docker'}

    #------------------------------------------
    # test load all required files to docker's current dir with user_files
    # then run analyzer in docker
    #------------------------------------------
    def test_ssmt_workitemmanager_user_files(self):
        expid = self.exp_id
        command = "python run_PopulationAnalyzer.py " + expid

        # upload 3 files to docker's current folder as linked file
        user_files = FileList(root='.', files_in_root=['PopulationAnalyzer.py', 'run_PopulationAnalyzer.py'])
        # user_files.add_file(os.path.join(self.par_par_dir, "simtools.ini"))

        platform = Platform('COMPS2')
        wi = SSMTWorkItem(item_name=self.wi_name, command=command, user_files=user_files,
                          related_experiments=[self.exp_id], tags=self.tags)
        wim = WorkItemManager(wi, platform)
        wim.process(check_status=True)
        self.validate(wi)

    #------------------------------------------
    # test load all required files to docker 'Assets' folder with asset_files
    # then run analyer in docker
    #------------------------------------------
    def test_ssmt_workitemmanager_asset_files(self):
        expid = self.exp_id
        command = "python Assets/run_PopulationAnalyzer.py " + expid
        asset_files = FileList()
        asset_files.add_file('PopulationAnalyzer.py')
        asset_files.add_file('run_PopulationAnalyzer.py')

        # upload simtools.ini to current dir in docker
        user_files = FileList()
        user_files.add_file(os.path.join(self.par_par_dir, "simtools.ini"))

        platform = Platform('COMPS2')
        wi = SSMTWorkItem(item_name=self.wi_name, command=command, asset_files=asset_files, user_files=user_files,
                          related_experiments=[self.exp_id], tags=self.tags)
        wim = WorkItemManager(wi, platform)
        wim.process(check_status=True)
        self.validate(wi)

    # ------------------------------------------
    # test another way to add files to docker with folder path under 'Assets' ie: Assets\analyzer
    # then run analyzer in docker
    # ------------------------------------------
    def test_ssmt_workitemmanager_with_input_folder(self):
        expid = self.exp_id
        command = "python run_PopulationAnalyzer1.py " + expid

        # add all files under 'analyzer' folder and put folder (relative_path) in docker
        asset_files = FileList()
        current_dir = os.path.abspath(os.path.dirname(__file__))
        assets_dir = os.path.join(current_dir, 'analyzer')
        # uncomment following line if you want to upload everything under 'analyzer' folder to remote
        #asset_files.add_path(assets_dir, relative_path="analyzer", recursive=True)

        # only upload 'PopulationAnalyzer.py' under analyzer folder to remote docker's Assets\analyzer folder
        asset_files.add_file(os.path.join(assets_dir, 'PopulationAnalyzer.py'), relative_path="analyzer")

        # upload simtools.ini and run_anaysis1.py files to current dir in docker
        user_files = FileList()
        user_files.add_file(os.path.join(self.par_par_dir, "simtools.ini"))
        user_files.add_file('run_PopulationAnalyzer1.py')

        platform = Platform('COMPS2')
        wi = SSMTWorkItem(item_name=self.wi_name, command=command, asset_files=asset_files, user_files=user_files,
                          related_experiments=[self.exp_id], tags=self.tags)
        wim = WorkItemManager(wi, platform)
        wim.process(check_status=True)
        self.validate(wi)

    # ------------------------------------------
    # test write analyzer result to dir in docker and retrieve it from there to local
    # then run analyzer in docker
    # ------------------------------------------
    def test_ssmt_workitemmanager_with_output_folder(self):
        expid = self.exp_id
        command = "python run_PopulationAnalyzer_with_output_folder.py " + expid

        # add all files under 'analyzer' folder and put folder (relative_path) in docker
        asset_files = FileList()
        current_dir = os.path.abspath(os.path.dirname(__file__))
        assets_dir = os.path.join(current_dir, 'analyzer')

        # only upload 'PopulationAnalyzer.py' under analyzer folder to remote docker's Assets\analyzer folder
        asset_files.add_file(os.path.join(assets_dir, 'PopulationAnalyzer_with_output_folder.py'), relative_path="analyzer")

        # upload simtools.ini and run_anaysis1.py files to current dir in docker
        user_files = FileList()
        user_files.add_file(os.path.join(self.par_par_dir, "simtools.ini"))
        user_files.add_file('run_PopulationAnalyzer_with_output_folder.py')

        platform = Platform('COMPS2')
        wi = SSMTWorkItem(item_name=self.wi_name, command=command, asset_files=asset_files, user_files=user_files,
                          related_experiments=[self.exp_id], tags=self.tags)
        wim = WorkItemManager(wi, platform)
        wim.process(check_status=True)
        self.validate(wi, output_path='output')

    # ------------------------------------------
    # test run multiple analyzers in docker
    # then run analyzer in docker
    # ------------------------------------------
    def test_ssmt_workitemmanager_with_multiple_analyzers(self):
        import pandas
        expid = self.exp_id
        command = "python run_2analyers.py " + expid

        # add all files under 'analyzer' folder and put folder (relative_path) in docker
        user_files = FileList(root='.', files_in_root=['PopulationAnalyzer.py', 'TimeseriesAnalyzer.py', 'run_2analyers.py'])
        user_files.add_file(os.path.join(self.par_par_dir, "simtools.ini"))

        platform = Platform('COMPS2')
        wi = SSMTWorkItem(item_name=self.wi_name, command=command, user_files=user_files,
                          related_experiments=[self.exp_id], tags=self.tags)
        wim = WorkItemManager(wi, platform)
        wim.process(check_status=True)

        self.workitem_id = wi.uid
        wi = WorkItem.get(wi.uid)

        # validate timeseries.csv from analyzer output
        output_file = "timeseries.csv"
        timeseries_csv = wi.retrieve_output_files([os.path.join("output", output_file)])
        del_file(output_file)
        with open(output_file, 'wb') as file:
            file.write(timeseries_csv[0])
        data = pandas.read_csv(output_file, skiprows=1, header=None).transpose()
        self.assertIsNotNone(data)

    #------------------------------------------
    # validate results from analyzer output against each simulation's insetChart.json
    #------------------------------------------
    def validate(self, wi, output_path=None):
        # # get workitem
        self.workitem_id = wi.uid
        wi = WorkItem.get(wi.uid)
        print("workitem id :" + str(wi.id))
        #wi_id = '95ce3908-955d-e911-9413-0050569e0ef3'
        #wi = WorkItem.get(wi_id)

        #delte results.json file first before same a new one
        del_file("results.json")
        # retriever 'results.json' file from Output tab of workitem and save to local disk
        if output_path is None:
            barr_out = wi.retrieve_output_files(['results.json'])
        else: # if output has folder, retriever from there
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


if __name__ == "__main__":
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='reports'))
