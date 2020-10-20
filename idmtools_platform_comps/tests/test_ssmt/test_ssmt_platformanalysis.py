import functools
import tempfile
import allure
import json
import os
import sys
import pytest

from idmtools.assets import AssetCollection
from idmtools_platform_comps import __version__ as platform_comps_version
from idmtools import __version__ as core_version
from idmtools.analysis.platform_anaylsis import PlatformAnalysis
from idmtools.core.platform_factory import Platform
from idmtools_test.utils.decorators import run_in_temp_dir
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools.core import ItemType, TRUTHY_VALUES

analyzer_path = os.path.join(os.path.dirname(__file__), "..", "inputs")
sys.path.insert(0, analyzer_path)
from simple_analyzer import SimpleAnalyzer  # noqa
from csv_analyzer import CSVAnalyzer  # noqa
from infectiousness_csv_analyzer import InfectiousnessCSVAnalyzer  # noqa
from node_csv_analyzer import NodeCSVAnalyzer  # noqa

comps_package_filename = f"idmtools_platform_comps-{platform_comps_version.replace('nightly.0', 'nightly')}.tar.gz"
core_package_filename = f"idmtools-{core_version.replace('nightly.0', 'nightly')}.tar.gz"
comps_local_package = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../dist/{comps_package_filename}"))
core_local_package = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../../idmtools_core/dist/{core_package_filename}"))
shell_script = f"""
export PYTHONPATH=$(pwd)/Assets/site-packages:$(pwd)/Assets/:$PYTHONPATH

pip install Assets/{core_package_filename} --force --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
pip install Assets/{comps_package_filename} --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple

$*
"""
# When enabled, ssmt tests will attempt to upload packages from local environment and install before run. You need to rebuild the the packages when code changes using pymake dist in the idmtools_core and ./idmtools_platform_comps directories
test_with_new_code = os.environ.get("TEST_WITH_PACKAGES", 'n').lower() in TRUTHY_VALUES


@functools.lru_cache(1)
def write_wrapper_script():
    f = tempfile.NamedTemporaryFile(suffix='.sh', mode='wb', delete=False)
    f.write(shell_script.replace("\r", "").encode('utf-8'))
    f.flush()
    return f.name


@pytest.mark.comps
@pytest.mark.ssmt
@allure.story("COMPS")
@allure.story("Analyzers")
@allure.story("PlatformAnalysis")
@allure.story("SSMT")
@allure.suite("idmtools_platform_comps")
class TestPlatformAnalysis(ITestWithPersistence):

    def setUp(self):
        print(self._testMethodName)
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)
        self.platform = Platform('COMPS2')
        self.tags = {'idmtools': self._testMethodName, 'WorkItem type': 'Docker'}
        self.input_file_path = analyzer_path

    # Test SimpleAnalyzer with SSMTAnalysis which analyzes python experiment's results
    def do_simple_python_analysis(self, platform):
        experiment_id = '9311af40-1337-ea11-a2be-f0921c167861'  # comps2 exp id
        # experiment_id = 'de07f612-69ed-ea11-941f-0050569e0ef3'  # idmtvapp17
        extra_args = dict()
        wrapper = None
        if test_with_new_code:
            wrapper = write_wrapper_script()
            extra_args['wrapper_shell_script'] = wrapper
            extra_args['asset_files'] = [core_local_package, comps_local_package]
        analysis = PlatformAnalysis(platform=platform, experiment_ids=[experiment_id], analyzers=[SimpleAnalyzer], analyzers_args=[{'filenames': ['config.json']}], analysis_name=self.case_name, tags={'idmtools': self._testMethodName, 'WorkItem type': 'Docker'}, **extra_args)

        analysis.analyze(check_status=True)
        wi = analysis.get_work_item()

        # verify workitem result
        local_output_path = "output"
        out_filenames = ["output/aggregated_config.json", "WorkOrder.json"]
        platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

        file_path = os.path.join(local_output_path, wi.id)
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", "aggregated_config.json")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "WorkOrder.json")))
        worker_order = json.load(open(os.path.join(file_path, "WorkOrder.json"), 'r'))
        self.assertEqual(worker_order['WorkItem_Type'], "DockerWorker")
        execution = worker_order['Execution']
        if test_with_new_code:
            self.assertEqual(execution['Command'], f"/bin/bash {os.path.basename(wrapper)} python platform_analysis_bootstrap.py --experiment-ids {experiment_id} --analyzers simple_analyzer.SimpleAnalyzer --block {platform._config_block}")
        else:
            self.assertEqual(execution['Command'], f"python platform_analysis_bootstrap.py --experiment-ids {experiment_id} --analyzers simple_analyzer.SimpleAnalyzer --block {platform._config_block}")

    @pytest.mark.smoke
    def test_ssmt_workitem_python_simple_analyzer_using_alias(self):
        self.do_simple_python_analysis(self.platform)

    @run_in_temp_dir
    @pytest.mark.serial
    def test_ssmt_using_aliases(self):
        p = Platform("BAYESIAN")
        self.do_simple_python_analysis(p)

    # Test CSVAnalyzer with SSMTAnalysis which analyzes python experiment's results
    def test_ssmt_workitem_python_csv_analyzer(self):
        experiment_id = '9311af40-1337-ea11-a2be-f0921c167861'  # comps2 exp id
        # experiment_id = 'de07f612-69ed-ea11-941f-0050569e0ef3'  # idmtvapp17
        extra_args = dict()
        wrapper = None
        if test_with_new_code:
            wrapper = write_wrapper_script()
            extra_args['wrapper_shell_script'] = write_wrapper_script()
            extra_args['asset_files'] = [core_local_package, comps_local_package]
        analysis = PlatformAnalysis(platform=self.platform, experiment_ids=[experiment_id], analyzers=[CSVAnalyzer], analyzers_args=[{'filenames': ['output/c.csv'], 'parse': True}], analysis_name=self.case_name, tags={'idmtools': self._testMethodName, 'WorkItem type': 'Docker'}, **extra_args)

        analysis.analyze(check_status=True)
        wi = analysis.get_work_item()

        # verify workitem result
        local_output_path = "output"
        out_filenames = ["output/aggregated_c.csv", "WorkOrder.json"]
        self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

        file_path = os.path.join(local_output_path, wi.id)
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", "aggregated_c.csv")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "WorkOrder.json")))
        worker_order = json.load(open(os.path.join(file_path, "WorkOrder.json"), 'r'))
        print(worker_order)
        self.assertEqual(worker_order['WorkItem_Type'], "DockerWorker")
        execution = worker_order['Execution']
        if test_with_new_code:
            self.assertEqual(execution['Command'], f"/bin/bash {os.path.basename(wrapper)} python platform_analysis_bootstrap.py --experiment-ids {experiment_id} --analyzers csv_analyzer.CSVAnalyzer --block COMPS2")
        else:
            self.assertEqual(execution['Command'], f"python platform_analysis_bootstrap.py --experiment-ids {experiment_id} --analyzers csv_analyzer.CSVAnalyzer --block COMPS2")

    @pytest.mark.comps
    def test_ssmt_seir_model_analysis(self):
        exp_id = "a980f265-995e-ea11-a2bf-f0921c167862"  # comps2 exp id
        # exp_id = "b2a31828-78ed-ea11-941f-0050569e0ef3"  # idmtvapp17
        filenames = {'filenames': ['output/individual.csv']}
        filenames_2 = {'filenames': ['output/node.csv']}
        extra_args = dict()
        wrapper = None
        if test_with_new_code:
            wrapper = write_wrapper_script()
            extra_args['wrapper_shell_script'] = wrapper
            extra_args['asset_files'] = [core_local_package, comps_local_package]
        analysis = PlatformAnalysis(platform=self.platform, experiment_ids=[exp_id], analyzers=[InfectiousnessCSVAnalyzer, NodeCSVAnalyzer], analyzers_args=[filenames, filenames_2], analysis_name=self.case_name, tags={'idmtools': self._testMethodName, 'WorkItem type': 'Docker'}, **extra_args)

        analysis.analyze(check_status=True)
        wi = analysis.get_work_item()

        # Verify workitem results
        local_output_path = "output"
        out_filenames = [exp_id + "/InfectiousnessCSVAnalyzer.csv", exp_id + "/NodeCSVAnalyzer.csv", "WorkOrder.json"]
        self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

        file_path = os.path.join(local_output_path, str(wi.uid))
        self.assertTrue(os.path.exists(os.path.join(file_path, exp_id, "InfectiousnessCSVAnalyzer.csv")))
        self.assertTrue(os.path.exists(os.path.join(file_path, exp_id, "NodeCSVAnalyzer.csv")))
        worker_order = json.load(open(os.path.join(file_path, "WorkOrder.json"), 'r'))
        print(worker_order)
        self.assertEqual(worker_order['WorkItem_Type'], "DockerWorker")
        execution = worker_order['Execution']
        if test_with_new_code:
            self.assertEqual(execution['Command'], f"/bin/bash {os.path.basename(wrapper)} python platform_analysis_bootstrap.py --experiment-ids {exp_id} --analyzers infectiousness_csv_analyzer.InfectiousnessCSVAnalyzer,node_csv_analyzer.NodeCSVAnalyzer --block COMPS2")
        else:
            self.assertEqual(execution['Command'], f"python platform_analysis_bootstrap.py --experiment-ids {exp_id} --analyzers infectiousness_csv_analyzer.InfectiousnessCSVAnalyzer,node_csv_analyzer.NodeCSVAnalyzer --block COMPS2")

    @pytest.mark.comps
    def test_ssmt_seir_model_analysis_single_script(self):
        exp_id = "a980f265-995e-ea11-a2bf-f0921c167862"  # comps2 exp id
        # exp_id = "b2a31828-78ed-ea11-941f-0050569e0ef3"  # idmtvapp17
        filenames = {'filenames': ['output/individual.csv']}
        filenames_2 = {'filenames': ['output/node.csv']}

        # Initialize two analyser classes with the path of the output csv file
        from custom_csv_analyzer import InfectiousnessCSVAnalyzer, NodeCSVAnalyzer
        analyzers = [InfectiousnessCSVAnalyzer, NodeCSVAnalyzer]
        extra_args = dict()
        wrapper = None
        if test_with_new_code:
            wrapper = write_wrapper_script()
            extra_args['wrapper_shell_script'] = wrapper
            extra_args['asset_files'] = [core_local_package, comps_local_package]
        analysis = PlatformAnalysis(platform=self.platform, experiment_ids=[exp_id], analyzers=analyzers, analyzers_args=[filenames, filenames_2], analysis_name=self.case_name, tags={'idmtools': self._testMethodName, 'WorkItem type': 'Docker'}, **extra_args)

        analysis.analyze(check_status=True)
        wi = analysis.get_work_item()

        # Verify workitem results
        local_output_path = "output"
        out_filenames = [exp_id + "/InfectiousnessCSVAnalyzer.csv", exp_id + "/NodeCSVAnalyzer.csv", "WorkOrder.json"]
        self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

        file_path = os.path.join(local_output_path, str(wi.uid))
        self.assertTrue(os.path.exists(os.path.join(file_path, exp_id, "InfectiousnessCSVAnalyzer.csv")))
        self.assertTrue(os.path.exists(os.path.join(file_path, exp_id, "NodeCSVAnalyzer.csv")))
        worker_order = json.load(open(os.path.join(file_path, "WorkOrder.json"), 'r'))
        print(worker_order)
        self.assertEqual(worker_order['WorkItem_Type'], "DockerWorker")
        execution = worker_order['Execution']
        if test_with_new_code:
            self.assertEqual(execution['Command'], f"/bin/bash {os.path.basename(wrapper)} python platform_analysis_bootstrap.py --experiment-ids {exp_id} --analyzers custom_csv_analyzer.InfectiousnessCSVAnalyzer,custom_csv_analyzer.NodeCSVAnalyzer --block COMPS2")
        else:
            self.assertEqual(execution['Command'], "python platform_analysis_bootstrap.py --experiment-ids " + exp_id + " --analyzers custom_csv_analyzer.InfectiousnessCSVAnalyzer,custom_csv_analyzer.NodeCSVAnalyzer --block COMPS2")

    @pytest.mark.skipif(not os.path.exists(comps_local_package) or not os.path.exists(core_local_package), reason=f"To run this, you need both {comps_local_package} and {core_local_package}. You can create these files by running pymake dist in each package directory")
    def test_using_newest_code(self):
        """
        This test uploads local packages and installs them remotely before running allowing us to test change to core, or comps packages without needing a new docker image(mostly)

        """
        wrapper = write_wrapper_script()
        experiment_id = '9311af40-1337-ea11-a2be-f0921c167861'  # comps2 exp id

        def pre_load_func():
            print("!!!!!!!!!!!!!Preload executed!!!!!!!!!!!!!!!!!!")
            from idmtools import __version__ as core_version
            from idmtools_platform_comps import __version__ as comps_version
            print(f"Idmtools Core Version: {core_version}")
            print(f"Idmtools COMPS Version: {comps_version}")

        # load_idmtools = RequirementsToAssetCollection(local_wheels=)
        # ac_id = load_idmtools.run()
        analysis = PlatformAnalysis(platform=self.platform, experiment_ids=[experiment_id], analyzers=[SimpleAnalyzer], analyzers_args=[{'filenames': ['config.json']}], analysis_name=self.case_name, asset_files=AssetCollection([core_local_package, comps_local_package]), pre_run_func=pre_load_func,
                                    wrapper_shell_script=wrapper)

        analysis.analyze(check_status=True)
        wi = analysis.get_work_item()
        out_filenames = ["output/aggregated_config.json", "WorkOrder.json", "stdout.txt"]
        local_output_path = "output"
        self.assertTrue(wi.succeeded)
        self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)
        file_path = os.path.join(local_output_path, wi.id)
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", "aggregated_config.json")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "WorkOrder.json")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "stdout.txt")))
        worker_order = json.load(open(os.path.join(file_path, "WorkOrder.json"), 'r'))
        self.assertEqual(worker_order['WorkItem_Type'], "DockerWorker")
        execution = worker_order['Execution']
        self.assertEqual(execution['Command'], f'/bin/bash {os.path.basename(wrapper)} python platform_analysis_bootstrap.py --experiment-ids {experiment_id} --analyzers simple_analyzer.SimpleAnalyzer --pre-run-func pre_load_func --block COMPS2')

        with open(os.path.join(file_path, "stdout.txt"), 'r') as fin:
            stdout_contents = fin.read()

        self.assertIn("!!!!!!!!!!!!!Preload executed!!!!!!!!!!!!!!!!!!", stdout_contents)
        self.assertIn(f"Idmtools Core Version: {core_version}", stdout_contents)
        self.assertIn(f"Idmtools COMPS Version: {platform_comps_version}", stdout_contents)
