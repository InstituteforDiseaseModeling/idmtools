import allure
import hashlib
import json
import os
import unittest
import uuid
import diskcache as dc
from collections import defaultdict
import pytest
from idmtools.assets import Asset
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform, platform
from COMPS.Data import Experiment as COMPSExperiment, QueryCriteria
from logging import getLogger
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_test.utils.common_experiments import get_model1_templated_experiment
from idmtools_test.utils.utils import get_case_name

logger = getLogger()
# Enable Caching of experiment past one session. Useful for working with problems in validating output of experiment
cache = dc.Cache(os.getcwd() if os.getenv("CACHE_FIXTURES", "No").lower()[0] in ["y", "1"] else None)


@cache.memoize(expire=300)
def setup_command_no_asset(case_name, platform: str = 'SlurmStage'):
    bt = CommandTask("Assets\\hello_world.bat")
    experiment = Experiment.from_task(
        bt,
        name=case_name,
        tags=dict(
            test_type='No Assets'
        )
    )
    experiment.add_asset(Asset(content="echo Hello World", filename='hello_world.bat'))

    experiment.run(wait_until_done=True, platform=Platform(platform))
    if not experiment.succeeded:
        raise ValueError("Setup prep failed")
    return experiment.id


@cache.memoize(expire=300)
def setup_python_model_1(case_name, platform: str = 'SlurmStage'):
    platform = Platform(platform)
    e = get_model1_templated_experiment(case_name)
    builder = SimulationBuilder()
    builder.add_sweep_definition(
        JSONConfiguredPythonTask.set_parameter_partial("a"),
        range(0, 2)
    )

    # second way to sweep parameter 'b' is to use class setParam which basiclly doing same thing as param_update
    # method
    builder.add_sweep_definition(
        JSONConfiguredPythonTask.set_parameter_partial("b"),
        [i * i for i in range(1, 4, 2)]
    )
    # ------------------------------------------------------

    e.simulations.add_builder(builder)
    e.run(True, platform)
    if not e.succeeded:
        raise ValueError("Setup prep failed")
    return e.id


@pytest.mark.comps
@pytest.mark.smoke
@allure.story("COMPS")
@allure.suite("idmtools_platform_comps")
class TestExperimentOperations(unittest.TestCase):

    def setUp(self) -> None:
        self.case_name = get_case_name(os.path.basename(__file__) + "--" + self._testMethodName)
        self.platform = Platform("SlurmStage")

    def test_no_assets(self):
        setup_command_no_asset(self.case_name, "SlurmStage")

        # Ensure login is called
        with platform("SlurmStage"):
            # Call Experiments
            qc = QueryCriteria().select_children("tags").where_tag(
                [
                    'test_type=No Assets'
                ]
            )

            experiments = COMPSExperiment.get(query_criteria=qc)
            experiment = experiments[0]

            # load as idm object(testing both get and to_entity
            idm_experiment = Experiment.from_id(experiment.id)

            # check tags
            for e in [experiment, idm_experiment]:
                self.assertIn('test_name', e.tags)
                self.assertEqual(self.__class__.__name__, e.tags['test_name'])
                self.assertIn('test_type', e.tags)
                self.assertEqual('No Assets', e.tags['test_type'])

            # check empty asset collection
            self.assertEqual(0, idm_experiment.assets.count)
            self.assertIsNone(idm_experiment.assets.id)
            self.assertEqual(1, idm_experiment.simulation_count)
            self.assertEqual(0, idm_experiment.simulations[0].assets.count)

    @allure.story("Assets")
    @pytest.mark.serial
    def test_list_assets(self):
        """
        Test that the list assets with children
        Test that the list assets without children
        Test that download works
        Test that the list assets on children(sims) works
        Returns:

        """
        eid = setup_python_model_1(self.case_name, 'SlurmStage')

        e_p: Experiment = Experiment.from_id(eid)
        with self.subTest("test_list_assets_and_download_children"):
            assets = self.platform._experiments.list_assets(e_p, children=True)
            self.assertEqual(5, len(assets))
            totals = defaultdict(int)
            for asset in assets:

                out_dir = os.path.join(os.path.dirname(__file__), 'output')
                os.makedirs(out_dir, exist_ok=True)
                name = os.path.join(out_dir, asset.filename)
                asset.download_to_path(name)
                try:
                    with open(name, 'rb') as din:
                        content = din.read()
                        md5_hash = hashlib.md5()
                        md5_hash.update(content)
                        self.assertEqual(asset.checksum, uuid.UUID(md5_hash.hexdigest()))
                    totals[asset.filename] += 1
                # ensure we always delete file after test
                finally:
                    os.remove(name)
            # self.assertEqual(4, totals['idmtools_metadata.json'])
            self.assertEqual(4, totals['config.json'])
            self.assertEqual(1, totals['model1.py'])

        with self.subTest("test_list_assets_no_children"):
            assets = self.platform._experiments.list_assets(e_p)
            self.assertEqual(1, len(assets))
            self.assertEqual('model1.py', assets[0].filename)

        with self.subTest("test_list_assets_simulations"):
            for sim in e_p.simulations:
                assets = self.platform._simulations.list_assets(sim)
                self.assertEqual(1, len(assets))
                self.assertEqual('config.json', assets[0].filename)
                # self.assertEqual('idmtools_metadata.json', assets[1].filename)
                content = assets[0].content
                self.assertIsNotNone(content)
                config = json.loads(content.decode('utf-8'))
                for tag, value in sim.tags.items():
                    if tag in ['a', 'b']:
                        self.assertIn(tag, config)
                        self.assertEqual(value, str(config[tag]))

