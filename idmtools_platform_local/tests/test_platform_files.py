import os
from importlib import reload

import pytest

from idmtools.core import EntityStatus
from idmtools.core.PlatformFactory import Platform
from idmtools.managers import ExperimentManager
from idmtools_models.python import PythonExperiment
from idmtools_platform_local.docker.DockerOperations import DockerOperations
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.ITestWithPersistence import ITestWithPersistence
from idmtools_test.utils.confg_local_runner_test import reset_local_broker, get_test_local_env_overrides
from idmtools_test.utils.decorators import restart_local_platform


@pytest.mark.docker
class TestPlatformSimulations(ITestWithPersistence):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        reset_local_broker()
        from idmtools_platform_local.workers.brokers import setup_broker
        setup_broker()
        # ensure we start from no environment
        dm = DockerOperations()
        dm.cleanup(True)

        import idmtools_platform_local.tasks.create_experiement
        import idmtools_platform_local.tasks.create_simulation
        reload(idmtools_platform_local.tasks.create_experiement)
        reload(idmtools_platform_local.tasks.create_simulation)

    @restart_local_platform(silent=True, **get_test_local_env_overrides())
    def test_fetch_simulation_files(self):
        platform = Platform('Local_Staging')

        pe = PythonExperiment(name=self.case_name, model_path=os.path.join(COMMON_INPUT_PATH, "python",
                                                                           "realpath_verify.py"))

        pe.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}

        em = ExperimentManager(experiment=pe, platform=platform)
        em.run()
        em.wait_till_done()

        self.assertTrue(all([s.status == EntityStatus.SUCCEEDED for s in pe.simulations]))

        files_to_preview = ['StdOut.txt', 'Assets/realpath_verify.py']
        files = platform.get_assets_for_simulation(pe.simulations[0], files_to_preview)
        self.assertEqual(len(files), len(files_to_preview))
        for filename in files_to_preview:
            self.assertIn(filename, files)
            if filename == "StdOut.txt":  # variable output
                self.assertEqual(files[filename].decode('utf-8').strip(), f'/data/{pe.uid}/Assets')
            else:  # default compare the content of the files
                with open(os.path.join(COMMON_INPUT_PATH, "python", "realpath_verify.py"), 'r') as rpin:
                    self.assertEqual(files[filename].decode("utf-8").replace("\r\n", "\n"), rpin.read().replace("\r\n", "\n"))

        # TODO attempt to unify the content of this file across platforms
        # On Comps, this will return the path to the Simulation Assets directory, but on Local, it returns the REAL
        # path since it is a symlink
