import os
import allure
import pytest
import unittest
from idmtools.core import EntityStatus, TRUTHY_VALUES
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_platform_comps.utils.assetize_output.assetize_output import AssetizeOutput
from idmtools_platform_comps.utils.file_filter_workitem import AtLeastOneItemToWatch, CrossEnvironmentFilterNotSupport
from idmtools_platform_comps.utils.ssmt_utils.file_filter import is_file_excluded
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.comps import load_library_dynamically
from idmtools_test.utils.test_task import TestTask

TEST_WITH_NEW_CODE = os.environ.get("TEST_WITH_PACKAGES", 'n').lower() in TRUTHY_VALUES


@pytest.mark.comps
@allure.feature("AssetizeOutputs")
class TestAssetizeOutput(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        self.platform = Platform("COMPS2")

    @pytest.mark.smoke
    def test_experiment_can_be_watched(self):
        e = Experiment.from_task(task=TestTask())
        ao = AssetizeOutput()
        ao.from_items(e)
        self.assertEqual(1, len(ao.related_experiments))
        self.assertEqual(ao.related_experiments[0], e)

    @pytest.mark.smoke
    def test_exclude(self):
        patterns = ['**StdOut.txt', '**StdErr.txt', '**.log']
        dummy_files = [
            'ABc/StdOut.txt',
            'b.py',
            'ABc/stdOut.txt',
            'ABc/stderr.txt',
            'ABc/123/stdout.txt',
            'ABc/123/stdout.err',
            'ABc/123/StdErr.err',
            'comps.log',
            'logs/idmtools.log'
        ]
        filtered_list = [f for f in dummy_files if not is_file_excluded(f, patterns)]
        self.assertEqual(len(filtered_list), 3)
        self.assertIn('b.py', filtered_list)
        self.assertIn('ABc/123/stdout.err', filtered_list)
        self.assertIn('ABc/123/StdErr.err', filtered_list)

    @pytest.mark.smoke
    def test_experiment_precreate_fails_if_no_watched_items(self):
        ao = AssetizeOutput()
        self.assertEqual(0, len(ao.related_experiments))
        with self.assertRaises(AtLeastOneItemToWatch) as er:
            ao.pre_creation(self.platform)
        self.assertEqual(er.exception.args[0], "You must specify at least one item to watch")

    # Skip this test until it can be rewritten using actual experiments or mocking some internal functions. At moment, it fails because it tries to retrieve the task from COMPS and it does not exist
    @pytest.mark.smoke
    @pytest.mark.serial
    def test_experiment_default_pattern_if_none_specified(self):
        exp_id = "9311af40-1337-ea11-a2be-f0921c167861"
        e = Experiment.from_id(f'{exp_id}', platform=self.platform)
        e.simulations[0].status = EntityStatus.CREATED
        ao = AssetizeOutput()
        ao.from_items(e)
        self.assertEqual(1, len(ao.related_experiments))
        self.assertEqual(ao.related_experiments[0], e)
        ao.pre_creation(self.platform)
        self.assertEqual(1, len(ao.file_patterns))
        self.assertEqual("**", ao.file_patterns[0])
        print(e.id)
        self.assertEqual(ao.create_command(), f'python3 Assets/assetize_ssmt_script.py --file-pattern "**" --exclude-pattern "StdErr.txt" "StdOut.txt" "WorkOrder.json" "*.log" --simulation-prefix-format-str "{{simulation.id}}" --asset-tag "AssetizedOutputfromFromExperiment={exp_id}"')
        ao.verbose = True
        self.assertEqual(ao.create_command(), f'python3 Assets/assetize_ssmt_script.py --file-pattern "**" --exclude-pattern "StdErr.txt" "StdOut.txt" "WorkOrder.json" "*.log" --simulation-prefix-format-str "{{simulation.id}}" --verbose --asset-tag "AssetizedOutputfromFromExperiment={exp_id}"')
        ao.clear_exclude_patterns()
        self.assertEqual(ao.create_command(), f'python3 Assets/assetize_ssmt_script.py --file-pattern "**" --simulation-prefix-format-str "{{simulation.id}}" --verbose --asset-tag "AssetizedOutputfromFromExperiment={exp_id}"')

        def pre_run_dummy():
            pass

        def entity_filter_dummy(item):
            return True

        def another_pre_run_dummy():
            pass
        ao.pre_run_functions.append(pre_run_dummy)
        ao.entity_filter_function = entity_filter_dummy
        ao.pre_creation(self.platform)
        self.assertEqual(len(ao.assets), 7 if TEST_WITH_NEW_CODE else 5)
        self.assertIn("pre_run.py", [f.filename for f in ao.assets])
        self.assertIn("entity_filter_func.py", [f.filename for f in ao.assets])
        self.assertEqual(ao.create_command(), f'python3 Assets/assetize_ssmt_script.py --file-pattern "**" --simulation-prefix-format-str "{{simulation.id}}" --pre-run-func pre_run_dummy --entity-filter-func entity_filter_dummy --verbose --asset-tag "AssetizedOutputfromFromExperiment={exp_id}"')

        ao.pre_run_functions.append(another_pre_run_dummy)
        self.assertEqual(ao.create_command(),
                         f'python3 Assets/assetize_ssmt_script.py --file-pattern "**" --simulation-prefix-format-str "{{simulation.id}}" --pre-run-func pre_run_dummy --pre-run-func another_pre_run_dummy --entity-filter-func entity_filter_dummy --verbose --asset-tag "AssetizedOutputfromFromExperiment={exp_id}"')

    def test_comps_simple(self):
        task = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"), parameters=dict(a=1))
        e = Experiment.from_task(name=self.case_name, task=task)
        ao = AssetizeOutput(name=self.case_name, verbose=True)
        if TEST_WITH_NEW_CODE:
            ao.add_pre_creation_hook(load_library_dynamically)
        ao.from_items(e)
        ao.run(wait_on_done=True, platform=self.platform)

        self.assertTrue(e.succeeded)
        self.assertTrue(ao.succeeded)

    def test_simulations_tags_prefix(self):
        """
        Confirm that we can use tags in the prefix format str

        Returns:

        """
        task = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"), parameters=dict(a=1))
        e = Experiment.from_task(name=self.case_name, task=task)
        e.simulations.items[0].tags['index'] = 1
        ao = AssetizeOutput(name=self.case_name, verbose=True, simulation_prefix_format_str='{simulation.tags["index"]}')
        ao.from_items(e)
        if TEST_WITH_NEW_CODE:
            ao.add_pre_creation_hook(load_library_dynamically)
        ao.run(wait_on_done=True, platform=self.platform)

        self.assertTrue(e.succeeded)
        self.assertTrue(ao.succeeded)
        #
        assets = [a.short_remote_path() for a in ao.asset_collection]
        self.assertIn('1/config.json', assets)
        self.assertIn('1/output/result.json', assets)

    def test_experiment_all(self):
        ao = AssetizeOutput(name=self.case_name, related_experiments=['9311af40-1337-ea11-a2be-f0921c167861'], verbose=True)
        if TEST_WITH_NEW_CODE:
            ao.add_pre_creation_hook(load_library_dynamically)
        ac = ao.run(wait_on_done=True, platform=self.platform)

        self.assertTrue(ao.succeeded)
        self.assertIsNotNone(ac)

        self.assertEqual(ac, ao.asset_collection)
        filelist = [f.filename for f in ac]
        self.assertEqual(36, len(filelist))

    def test_experiment_duplicate_error(self):
        ao = AssetizeOutput(name=self.case_name, related_experiments=['9311af40-1337-ea11-a2be-f0921c167861'], no_simulation_prefix=True)
        if TEST_WITH_NEW_CODE:
            ao.add_pre_creation_hook(load_library_dynamically)
        ao.run(wait_on_done=True, platform=self.platform)

        self.assertTrue(ao.failed)
        error_info = ao.fetch_error(print_error=False)
        self.assertIsInstance(error_info, dict)
        self.assertEqual(error_info["type"], "DuplicateAsset")
        self.assertEqual(error_info["doc_link"], "platforms/comps/assetize_output.html#errors")

    def test_experiment(self):
        ao = AssetizeOutput(name=self.case_name, related_experiments=['9311af40-1337-ea11-a2be-f0921c167861'], file_patterns=["**/a.csv"], verbose=True)
        if TEST_WITH_NEW_CODE:
            ao.add_pre_creation_hook(load_library_dynamically)
        ac = ao.run(wait_on_done=True, platform=self.platform)

        self.assertTrue(ao.succeeded)
        self.assertIsNotNone(ac)

        self.assertEqual(ac, ao.asset_collection)
        filelist = [f.filename for f in ac]
        self.assertEqual(9, len(filelist))

    def test_experiment_cross_environment_fail(self):
        ao = AssetizeOutput(name=self.case_name, related_experiments=['9311af40-1337-ea11-a2be-f0921c167861'], file_patterns=["**/a.csv"], verbose=True)
        with self.assertRaises(CrossEnvironmentFilterNotSupport) as err:
            ac = ao.run(wait_on_done=True, platform=Platform("SLURM2"))

        self.assertEqual('You cannot filter files between environment. In this case, the Experiment 9311af40-1337-ea11-a2be-f0921c167861 is in Bayesian but you are running your workitem in SlurmStage', err.exception.args[0])

    def test_experiment_sim_prefix(self):
        ao = AssetizeOutput(name=self.case_name, related_experiments=['9311af40-1337-ea11-a2be-f0921c167861'], simulation_prefix_format_str="{simulation.state}/{simulation.id}", file_patterns=["**/a.csv"], verbose=True)
        if TEST_WITH_NEW_CODE:
            ao.add_pre_creation_hook(load_library_dynamically)
        ac = ao.run(wait_on_done=True, platform=self.platform)

        self.assertTrue(ao.succeeded)
        self.assertIsNotNone(ac)

        self.assertEqual(ac, ao.asset_collection)
        filelist = [f.filename for f in ac]
        self.assertEqual(9, len(filelist))

    def test_simulation(self):
        ao = AssetizeOutput(name=self.case_name, related_simulations=['9d11af40-1337-ea11-a2be-f0921c167861'], file_patterns=["**/*.csv"], verbose=True)
        if TEST_WITH_NEW_CODE:
            ao.add_pre_creation_hook(load_library_dynamically)
        ac = ao.run(wait_on_done=True, platform=self.platform)

        self.assertTrue(ao.succeeded)
        self.assertIsNotNone(ac)

        self.assertEqual(ac, ao.asset_collection)
        filelist = [f.filename for f in ac]
        self.assertEqual(3, len(filelist))

    def test_workitem(self):
        ao = AssetizeOutput(name=self.case_name, related_work_items=['a6d11db7-1603-e911-80ca-f0921c167866'], file_patterns=["*.png"], verbose=True)
        if TEST_WITH_NEW_CODE:
            ao.add_pre_creation_hook(load_library_dynamically)
        ac = ao.run(wait_on_done=True, platform=self.platform)

        self.assertTrue(ao.succeeded)
        self.assertIsNotNone(ac)

        self.assertEqual(ac, ao.asset_collection)
        filelist = [f.filename for f in ac]
        self.assertEqual(1, len(filelist))

        with self.subTest("test_workitem_prefix"):

            ao2 = AssetizeOutput(name=self.case_name, related_work_items=['a6d11db7-1603-e911-80ca-f0921c167866', ao], file_patterns=["**.txt"], exclude_patterns=['WorkOrder.json'], verbose=True, work_item_prefix_format_str="{work_item.name}")
            if TEST_WITH_NEW_CODE:
                ao2.add_pre_creation_hook(load_library_dynamically)
            ac = ao2.run(wait_on_done=True, platform=self.platform)
            self.assertTrue(ao2.succeeded)
            self.assertIsNotNone(ac)

            self.assertEqual(ac, ao2.asset_collection)
            filelist = [f.filename for f in ac]
            self.assertEqual(4, len(filelist))

    def test_filter_ac(self):
        ao = AssetizeOutput(name=self.case_name, related_asset_collections=['2b53af74-2b4a-e711-80c1-f0921c167860'], file_patterns=["**/libvectorstats.dll"], verbose=True)
        if TEST_WITH_NEW_CODE:
            ao.add_pre_creation_hook(load_library_dynamically)
        ac = ao.run(wait_on_done=True, platform=self.platform)

        self.assertTrue(ao.succeeded)
        self.assertIsNotNone(ac)

        self.assertEqual(ac, ao.asset_collection)
        filelist = [f.filename for f in ac]
        self.assertEqual(1, len(filelist))

    def test_dry_run(self):
        ao = AssetizeOutput(name=self.case_name, related_simulations=['9d11af40-1337-ea11-a2be-f0921c167861'], related_asset_collections=['2b53af74-2b4a-e711-80c1-f0921c167860'], verbose=True, dry_run=True)
        if TEST_WITH_NEW_CODE:
            ao.add_pre_creation_hook(load_library_dynamically)
        ac = ao.run(wait_on_done=True, platform=self.platform)

        self.assertTrue(ao.succeeded)
        self.assertIsNone(ac)

    def test_simulation_include_assets(self):
        ao = AssetizeOutput(name=self.case_name, related_experiments=['874586c5-860a-eb11-a2c2-f0921c167862'], file_patterns=["**/*.py"], verbose=True, include_assets=True)
        if TEST_WITH_NEW_CODE:
            ao.add_pre_creation_hook(load_library_dynamically)
        ac = ao.run(wait_on_done=True, platform=self.platform)

        self.assertTrue(ao.succeeded)
        self.assertIsNotNone(ac)

        self.assertEqual(ac, ao.asset_collection)
        filelist = [f.filename for f in ac]
        self.assertEqual(60, len(filelist))
        py_files = [f for f in ac if f.filename.endswith('.py')]
        self.assertEqual(60, len(py_files))
