import allure
import datetime
import os
import time
import pytest
import unittest
from COMPS.Data import Experiment, QueryCriteria
from idmtools.core.platform_factory import Platform
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence


@pytest.mark.cleanup
@allure.story("COMPS")
@allure.story("Delete Items")
@allure.suite("idmtools_platform_comps")
class TestCleanup(ITestWithPersistence):

    # Enable this test by setting the environment variable CLEANUP_COMPS_TESTS to 1
    @pytest.mark.comps
    @unittest.skipIf(not os.getenv('CLEANUP_COMPS_TESTS', '0') == '1', reason="CLEANUP_COMPS_TESTS set to false")
    def test_delete_experiment_by_name_owner_date_tags(self):
        Platform('Bayesian', endpoint="https://comps2.idmod.org", environment="Bayesian")
        name = '%%,Owner=shchen'
        # name = '%Test%,Owner=shchen'  # name contains Test, and Owner is shchen
        opr = '~' if '%' in name else '='
        qc = ['name{}{}'.format(opr, name), 'date_created<={}'.format(self.get_comps_start_ndays_ago(7))]  # 7 days ago
        # ee = Experiment.get(query_criteria=QueryCriteria().where(qc)  #filter by name and owner
        # filter: name contains anything, owner=shchen, AND tag key with 'idmtools'
        ee = Experiment.get(query_criteria=QueryCriteria().where(qc).select_children('tags').where_tag(['idmtools']))
        print("total experiments to delete", len(ee))
        for e in ee:
            print("Deleting experiment :" + str(e.id))
            self.delete_experiment_by_id(e.id)

    def get_comps_start_datetime(self, day):
        start_datetime = datetime.datetime.strptime(day, "%Y-%m-%d").date()
        utcdt = datetime.datetime.utcfromtimestamp(time.mktime(start_datetime.timetuple()))
        return utcdt.strftime('%Y-%m-%dT%H:%M:%S')

    def get_comps_start_ndays_ago(self, ndays):
        # start_datetime = datetime.date.today()
        start_datetime = datetime.datetime.utcnow() - datetime.timedelta(ndays)
        utcdt = datetime.datetime.utcfromtimestamp(time.mktime(start_datetime.timetuple()))
        return utcdt.strftime('%Y-%m-%dT%H:%M:%S')

    def delete_experiment_by_id(self, id):
        try:
            ee = Experiment.get(id)
        except:  # noqa E722
            ee = None
        ee.delete()
        self.assert_experiment_not_exists(id)

    def assert_experiment_not_exists(self, id):
        with self.assertRaises(RuntimeError) as context:
            ee = Experiment.get(id)  # noqa F841
        self.assertTrue('404 NotFound - Failed to retrieve experiment for given id' in str(context.exception.args[0]))
