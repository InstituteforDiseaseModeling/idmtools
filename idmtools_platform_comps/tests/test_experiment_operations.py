import os
import re
import unittest
import pytest
import responses
from _pytest.config import get_config
from idmtools import IdmConfigParser
from idmtools.core.platform_factory import Platform, platform
from COMPS.Data import Experiment as COMPSExperiment, QueryCriteria
from tests.utils import load_fixture
from functools import partial
from logging import getLogger

from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment

logger = getLogger()
# Enable Creation of Experiments used for fixtures. Use when recreating fixtures
ce = os.getenv('CREATE_EXPERIMENTS', 'No')
CREATE_EXPERIMENTS = ce and ce[0].lower() in ['y', 't', '1']
# Overwrite existing fixtures
of = os.getenv('OVERWRITE_FIXTURES', 'No')
OVERWRITE_FIXTURES = of and of[0].lower() in ['y', 't', '1']
cfne = os.getenv('CREATE_IF_NOT_EXIST', 'No')
CREATE_IF_NOT_EXIST = cfne and cfne[0].lower() in ['y', 't', '1']
mark_expr = get_config().getoption('markexpr')


def is_label_enabled(label):
    # is comps label enabled in testing?
    if mark_expr and (label in mark_expr and f'not {label}' not in mark_expr):
        return True
    elif not mark_expr:
        return True


is_comps_enabled = is_label_enabled("comps")


# Only Run when
# We are using only fixtures or
# CREATE_IF_NOT_EXIST or OVERWRITE_FIXTURES are true and (mark_expr and
#                     ('comps' in mark_expr and 'not comps' not in mark_expr)
@pytest.mark.skipif(not is_comps_enabled and not (CREATE_IF_NOT_EXIST or OVERWRITE_FIXTURES),
                    reason="Creation of fixtures enabled but COMPS disabled")
class TestExperimentOperations(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        if CREATE_EXPERIMENTS:
            """
            This code should only run when creation in enabled. Only use in development when changing internal 
            experiment operations that change change requests to COMPS, when re-building fixtures, or when doing full
            integration tests
            """
            logger.info('Creating Experiment')
            cls.setup_responses()

            with platform("COMPS2"):
                # task with no assets(command line task)
                bt = CommandTask('dir')
                experiment = Experiment.from_task(
                    bt,
                    tags=dict(
                        test_name=cls.__name__,
                        test_type='No Assets'
                    )
                )

                experiment.run()
                print(experiment.id)

                bt = CommandTask('dir.exe')

    @classmethod
    def setup_responses(cls):
        endpoint = IdmConfigParser.get_option("COMPS2", "endpoint")
        # enable fixtures for Experiments and tokens
        for method in [responses.GET, responses.POST]:
            responses.add_callback(
                method, re.compile(f'{endpoint}/api/(tokens|Experiments|Simulations)(.*)'),
                callback=partial(
                    load_fixture,
                    create_if_not_exist=CREATE_IF_NOT_EXIST,
                    overwrite_fixtures=OVERWRITE_FIXTURES
                )
            )

    @responses.activate
    def test_no_assets(self):

        self.setup_responses()
        # Ensure login is called
        with platform("COMPS2"):

            # Call Experiments
            qc = QueryCriteria().select_children("tags").where_tag(
                [
                    f'test_name={self.__class__.__name__}',
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
            self.assertEquals(0, idm_experiment.assets.count)
            self.assertIsNone(idm_experiment.assets.id)
            self.assertEquals(1, idm_experiment.simulation_count)
            self.assertEquals(0, idm_experiment.simulations[0].assets.count)


