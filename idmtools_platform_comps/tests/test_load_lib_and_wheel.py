import allure
import os
import sys
from pathlib import Path
import pytest
from idmtools.assets import AssetCollection, Asset
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_platform_comps.utils.package_version import get_latest_pypi_package_version_from_artifactory, get_versions_from_site, get_pypi_package_versions_from_artifactory
from idmtools_platform_comps.utils.python_requirements_ac.requirements_to_asset_collection import RequirementsToAssetCollection
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.utils import del_folder, get_case_name

model_path = os.path.join(os.path.dirname(__file__), "inputs", "simple_load_lib_example")
sys.path.insert(0, model_path)


@pytest.mark.comps
@pytest.mark.python
@allure.story("COMPS")
@allure.story("Python")
@allure.story("Requirements to Asset Collection")
@allure.suite("idmtools_platform_comps")
class TestLoadLibWheel(ITestWithPersistence):

    def setUp(self) -> None:
        self.case_name = get_case_name(os.path.basename(__file__) + "--" + self._testMethodName)
        print(self.case_name)
        self.platform = Platform('COMPS2')

    @pytest.mark.smoke
    def test_get_latest_package_and_get_packages(self):
        package = get_latest_pypi_package_version_from_artifactory('numpy')
        self.assertIsNotNone(package)

        package = get_latest_pypi_package_version_from_artifactory('numpy', base_version="1.18")
        self.assertEqual(package, '1.18.5')

        package = get_latest_pypi_package_version_from_artifactory('statsmodels')
        self.assertIsNotNone(package)

        package = get_pypi_package_versions_from_artifactory('statsmodels')
        self.assertIsNotNone(package)
        self.assertIsInstance(package, list)
        self.assertEqual(package[-1], '0.4.0')

        package = get_pypi_package_versions_from_artifactory('statsmodels', exclude_pre_release=False)
        self.assertIsNotNone(package)
        self.assertIsInstance(package, list)
        self.assertEqual(package[-1], '0.4.0')

        package = get_pypi_package_versions_from_artifactory('statsmodels', base_version="0.5", exclude_pre_release=False)
        self.assertIsNotNone(package)
        self.assertEqual(2, len(package))
        self.assertIsInstance(package, list)
        self.assertEqual(package[-1], '0.5.0rc1')

    @pytest.mark.smoke
    def test_get_latest_package_idm(self):
        package = get_latest_pypi_package_version_from_artifactory('idmtools')
        self.assertIsNotNone(package)

        package = get_latest_pypi_package_version_from_artifactory('idmtools', base_version="1.5")
        self.assertEqual(package, '1.5.1')

        package = get_pypi_package_versions_from_artifactory('idmtools')
        self.assertIsNotNone(package)
        self.assertIsInstance(package, list)
        self.assertEqual(package[-1], '0.2.0')

        package = get_latest_pypi_package_version_from_artifactory('idmtools-platform-comps')
        self.assertIsNotNone(package)

        package = get_latest_pypi_package_version_from_artifactory('idmtools-platform-comps', base_version="1.5")
        self.assertEqual(package, '1.5.2')

        package = get_pypi_package_versions_from_artifactory('rse-api')
        self.assertIsNotNone(package)
        self.assertIsInstance(package, list)
        self.assertEqual(package[-1], '1.0.0')

        package = get_pypi_package_versions_from_artifactory('rse-db')
        self.assertIsNotNone(package)
        self.assertIsInstance(package, list)
        self.assertEqual(package[-1], '1.0.0')

        package = get_pypi_package_versions_from_artifactory('dtk-tools')
        self.assertIsNotNone(package)
        self.assertIsInstance(package, list)
        self.assertEqual(package[-1], '1.0.0')

    @pytest.mark.long
    @pytest.mark.comps
    def test_requirements_to_assetcollection_ignores_platform_num_cores(self):
        # ------------------------------------------------------
        # First load 'zipp' package (note: comps does not have 'zipp' package)
        # ------------------------------------------------------
        requirements_path = os.path.join(model_path, 'requirements.txt')
        pL = Platform('SLURM2', num_cores=2)
        rta = RequirementsToAssetCollection(name=self.case_name, platform=pL, requirements_path=requirements_path)
        ac_id = rta.run(rerun=True)

        self.assertIsNotNone(ac_id)

    @pytest.mark.long
    @pytest.mark.comps
    @pytest.mark.serial
    def test_exp_with_load_zipp_lib(self):
        # ------------------------------------------------------
        # First load 'zipp' package (note: comps does not have 'zipp' package)
        # ------------------------------------------------------
        requirements_path = os.path.join(model_path, 'requirements.txt')
        pl = RequirementsToAssetCollection(name=self.case_name, platform=self.platform, requirements_path=requirements_path)
        ac_id = pl.run(rerun=True)
        common_assets = AssetCollection.from_id(ac_id, platform=self.platform, as_copy=True)

        # create python task with script 'model_file.py', task is doing this in comps: "python ./Assets/zipp_file.py"
        script_path = os.path.join(model_path, 'zipp_file.py')
        task = JSONConfiguredPythonTask(script_path=script_path, common_assets=common_assets)

        # create experiment with 1 base simulation with python task
        experiment = Experiment(name=self.case_name, simulations=[task.to_simulation()])
        experiment.tags = {'ac_id': str(ac_id)}

        experiment.run(wait_until_done=True)

        # Make sure this experiment succeeded
        self.assertTrue(experiment.succeeded)

        # verify result
        sims = self.platform.get_children_by_object(experiment)
        local_output_path = "output"
        del_folder(local_output_path)
        out_filenames = ["StdOut.txt"]
        self.platform.get_files_by_id(sims[0].id, ItemType.SIMULATION, out_filenames, local_output_path)
        self.assertTrue(os.path.exists(os.path.join(local_output_path, sims[0].id, "StdOut.txt")))
        contents = Path(os.path.join(local_output_path, sims[0].id, "StdOut.txt")).read_text()
        self.assertEqual(contents, "b/\nb/d/\ng/h/\ng/\n")

    @pytest.mark.long
    @pytest.mark.comps
    def test_exp_without_load_required_zipp_lib(self):
        # ------------------------------------------------------
        # First NOT load 'zipp' package to test negative case, (to see if zipp_file.py script will fail in comps)
        # xmlrunner==1.7.7 here is loading a unrelated package to avoid empty packages for RequirementsToAssetCollection
        # ------------------------------------------------------
        pl = RequirementsToAssetCollection(name=self.case_name, platform=self.platform, requirements_path="", pkg_list=["xmlrunner==1.7.7"])
        ac_id = pl.run()
        common_assets = AssetCollection.from_id(ac_id, platform=self.platform, as_copy=True)

        # create python task with script 'model_file.py', task is doing this in comps: "python ./Assets/model_file.py"
        script_path = os.path.join(model_path, 'zipp_file.py')
        task = JSONConfiguredPythonTask(script_path=script_path, common_assets=common_assets)

        # create experiment with 1 base simulation with python task
        experiment = Experiment(name=self.case_name, simulations=[task.to_simulation()])
        experiment.tags = {'ac_id': str(ac_id)}
        experiment.run(wait_until_done=True)

        # Make sure this experiment failed
        self.assertFalse(experiment.succeeded)

        # verify result
        sims = self.platform.get_children_by_object(experiment)
        local_output_path = "output"
        del_folder(local_output_path)
        out_filenames = ["StdErr.txt"]
        self.platform.get_files_by_id(sims[0].id, ItemType.SIMULATION, out_filenames, local_output_path)
        self.assertTrue(os.path.exists(os.path.join(local_output_path, sims[0].id, "StdErr.txt")))
        contents = Path(os.path.join(local_output_path, sims[0].id, "StdErr.txt")).read_text()
        self.assertIn("ModuleNotFoundError: No module named 'zipp'", contents)

    @pytest.mark.long
    @pytest.mark.comps
    def test_exp_load_wheel(self):
        # ------------------------------------------------------
        # First load custom wheel with RequirementsToAssetCollection
        # ------------------------------------------------------
        requirements_path = os.path.join(model_path, 'requirements1.txt')
        local_wheels_path = [os.path.join(model_path, 'seaborn-0.7.1-py2.py3-none-any.whl')]
        pl = RequirementsToAssetCollection(name=self.case_name, platform=self.platform, requirements_path=requirements_path, local_wheels=local_wheels_path)
        ac_id = pl.run()
        common_assets = AssetCollection.from_id(ac_id, platform=self.platform, as_copy=True)

        # create python task with script 'seaborn_file.py', task is doing this in comps: "python ./Assets/seaborn_file.py"
        script_path = os.path.join(model_path, 'seaborn_file.py')
        task = JSONConfiguredPythonTask(script_path=script_path, common_assets=common_assets)

        ac = AssetCollection()
        model_asset = Asset(absolute_path=os.path.join(model_path, "tips.csv"))
        ac.add_asset(model_asset)
        # create experiment with 1 base simulation with python task
        experiment = Experiment(name=self.case_name, simulations=[task.to_simulation()], assets=ac)
        experiment.tags = {'ac_id': str(ac_id)}
        experiment.run(wait_until_done=True)

        # Make sure this experiment succeeded
        self.assertTrue(experiment.succeeded)

        # verify result
        sims = self.platform.get_children_by_object(experiment)
        local_output_path = "output"
        del_folder(local_output_path)
        out_filenames = ["tips.png"]
        self.platform.get_files_by_id(sims[0].id, ItemType.SIMULATION, out_filenames, local_output_path)
        self.assertTrue(os.path.exists(os.path.join(local_output_path, sims[0].id, "tips.png")))

    @pytest.mark.long
    @pytest.mark.comps
    def test_exp_with_load_pytest_lib_slurm(self):
        # ------------------------------------------------------
        # First load 'pytest' package (note: comps does not have 'pytest' package)
        # ------------------------------------------------------
        platform = Platform('SLURM2')
        requirements_path = os.path.join(model_path, 'requirements1.txt')
        pl = RequirementsToAssetCollection(name=self.case_name, platform=platform, requirements_path=requirements_path)
        ac_id = pl.run()
        common_assets = AssetCollection.from_id(ac_id, platform=platform, as_copy=True)

        # create python task with script 'zipp_file_slurm.py', task is doing this in comps: "python ./Assets/zipp_file_slurm.py"
        script_path = os.path.join(model_path, 'model_file.py')
        task = JSONConfiguredPythonTask(script_path=script_path, common_assets=common_assets)

        # create experiment with 1 base simulation with python task
        experiment = Experiment(name=self.case_name, simulations=[task.to_simulation()])
        experiment.tags = {'ac_id': str(ac_id)}
        experiment.run(wait_until_done=True)

        # Make sure this experiment succeeded
        self.assertTrue(experiment.succeeded)

    @pytest.mark.long
    @pytest.mark.comps
    @pytest.mark.smoke
    @pytest.mark.serial
    def test_exp_with_load_zipp_lib_slurm(self):
        # ------------------------------------------------------
        # First load 'zipp' package (note: comps does not have 'zipp' package)
        # ------------------------------------------------------
        platform = Platform('SLURM2')
        requirements_path = os.path.join(model_path, 'requirements.txt')
        pl = RequirementsToAssetCollection(name=self.case_name, platform=platform, requirements_path=requirements_path)
        ac_id = pl.run(rerun=True)
        common_assets = AssetCollection.from_id(ac_id, platform=platform, as_copy=True)

        # create python task with script 'zipp_file_slurm.py', task is doing this in comps: "python ./Assets/zipp_file_slurm.py"
        script_path = os.path.join(model_path, 'zipp_file_slurm.py')
        task = JSONConfiguredPythonTask(script_path=script_path, common_assets=common_assets)

        # create experiment with 1 base simulation with python task
        experiment = Experiment(name=self.case_name, simulations=[task.to_simulation()])
        experiment.tags = {'ac_id': str(ac_id)}
        experiment.run(wait_until_done=True)

        # Make sure this experiment succeeded
        self.assertTrue(experiment.succeeded)
        # verify result
        sims = self.platform.get_children_by_object(experiment)
        local_output_path = "output"
        del_folder(local_output_path)
        out_filenames = ["StdOut.txt"]
        self.platform.get_files_by_id(sims[0].id, ItemType.SIMULATION, out_filenames, local_output_path)
        self.assertTrue(os.path.exists(os.path.join(local_output_path, sims[0].id, "StdOut.txt")))
        contents = Path(os.path.join(local_output_path, sims[0].id, "StdOut.txt")).read_text()
        self.assertEqual(contents, "b/\nb/d/\ng/h/\ng/\n")

    @pytest.mark.long
    @pytest.mark.comps
    def test_exp_load_wheel_from_aritifactory(self):
        # ------------------------------------------------------
        # First load custom wheel with RequirementsToAssetCollection
        # ------------------------------------------------------
        requirements_path = os.path.join(model_path, 'requirements3.txt')
        pl = RequirementsToAssetCollection(name=self.case_name, platform=self.platform, requirements_path=requirements_path)
        ac_id = pl.run()
        common_assets = AssetCollection.from_id(ac_id, platform=self.platform, as_copy=True)

        # create python task with script 'seaborn_file.py', task is doing this in comps: "python ./Assets/seaborn_file.py"
        script_path = os.path.join(model_path, 'seaborn_file.py')
        task = JSONConfiguredPythonTask(script_path=script_path, common_assets=common_assets)

        ac = AssetCollection()
        model_asset = Asset(absolute_path=os.path.join(model_path, "tips.csv"))
        ac.add_asset(model_asset)
        # create experiment with 1 base simulation with python task
        experiment = Experiment(name=self.case_name, simulations=[task.to_simulation()], assets=ac)
        experiment.tags = {'ac_id': str(ac_id)}
        experiment.run(wait_until_done=True)

        # Make sure this experiment succeeded
        self.assertTrue(experiment.succeeded)

    @pytest.mark.long
    @pytest.mark.comps
    def test_regenerate_ac(self):
        # ------------------------------------------------------
        # First load custom wheel with RequirementsToAssetCollection
        # ------------------------------------------------------
        requirements_path = os.path.join(model_path, 'requirements3.txt')
        pl = RequirementsToAssetCollection(name=self.case_name, platform=self.platform, requirements_path=requirements_path)
        ac_id = pl.run(rerun=False)
        self.assertIsNotNone(ac_id)
        common_assets = AssetCollection.from_id(ac_id, platform=self.platform, as_copy=True)

        # create python task with script 'seaborn_file.py', task is doing this in comps: "python ./Assets/seaborn_file.py"
        script_path = os.path.join(model_path, 'seaborn_file.py')
        task = JSONConfiguredPythonTask(script_path=script_path, common_assets=common_assets)

        ac = AssetCollection()
        model_asset = Asset(absolute_path=os.path.join(model_path, "tips.csv"))
        ac.add_asset(model_asset)
        # create experiment with 1 base simulation with python task
        experiment = Experiment(name=self.case_name, simulations=[task.to_simulation()], assets=ac)
        experiment.tags = {'ac_id': str(ac_id)}
        experiment.run(wait_until_done=True)

        # Make sure this experiment succeeded
        self.assertTrue(experiment.succeeded)
