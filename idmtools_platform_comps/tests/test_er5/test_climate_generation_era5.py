import os
import unittest
import shutil
import tempfile
import xmlrunner
import pytest

from idmtools.core.platform_factory import Platform
from idmtools.core import ItemType
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem

from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.utils import get_case_name


@pytest.mark.ssmt
@pytest.mark.comps
class ClimateGenerationTest(ITestWithPersistence):

    def setUp(self):
        self.case_name = get_case_name(os.path.basename(__file__) + "--" + self._testMethodName)
        self.platform = Platform('BAYESIAN')

    # ------------------------------------------
    # test generate ERA5 climate files
    # ------------------------------------------
    @pytest.mark.comps
    @pytest.mark.long
    def test_generate_era5_climate_files(self):
        # A .csv or a demographics file containing input coordinates
        points_file = 'site_details.csv'

        # Start/end dates in one of the formats: year (2015) or year and day-of-year (2015032) or year-month-day (20150201)
        start_date = 2010
        end_date = 2012

        # Optional arguments
        optional_args = '--id-ref default --node-col id --create-asset'

        # Prepare the work item (NOT to be modified).
        docker_image = "weather-files:1.1"  # Specify the weather-tool docker image instead to use
        command_pattern = "python /app/generate_weather_asset_collection.py {} {} {} {}"
        command = command_pattern.format(points_file, start_date, end_date, optional_args)

        wi = SSMTWorkItem(item_name=self.case_name, docker_image=docker_image, command=command)
        # upload site_details.csv to workitem's root dir in COMPS
        wi.transient_assets.add_asset(os.path.join("climate", points_file))
        wi.run(wait_on_done=True)

        # Get the work item, related asset collection, and assets
        wi_id = wi.id
        print(wi_id)
        self.validate(wi_id)

    # ------------------------------------------
    # test generate ERA5 climate files with WorkOrder.json
    # ------------------------------------------
    @pytest.mark.comps
    @pytest.mark.long
    def test_generate_era5_climate_files_wb_workolder(self):
        wi = SSMTWorkItem(item_name=self.case_name, command="anything")
        # upload site_details.csv to workitem's root dir in COMPS
        wi.transient_assets.add_asset(os.path.join("climate", "site_details.csv"))
        # upload WorkOrder.json to workitem's root dir in COMPS
        wi.load_work_order(os.path.join("climate", "WorkOrder.json"))
        wi.run(wait_on_done=True)

        # Get the work item, related asset collection, and assets
        wi_id = wi.id
        print(wi_id)
        self.validate(wi_id)

    def validate(self, wi_id):
        try:
            out_filenames = [
                'out/dtk_15arcmin_air_temperature_daily.bin',
                'out/dtk_15arcmin_air_temperature_daily.bin.json',
                'out/dtk_15arcmin_land_temperature_daily.bin',
                'out/dtk_15arcmin_land_temperature_daily.bin.json',
                'out/dtk_15arcmin_rainfall_daily.bin',
                'out/dtk_15arcmin_rainfall_daily.bin.json',
                'out/dtk_15arcmin_relative_humidity_daily.bin',
                'out/dtk_15arcmin_relative_humidity_daily.bin.json'
            ]
            output_path = tempfile.mkdtemp()
            self.platform.get_files_by_id(wi_id, ItemType.WORKFLOW_ITEM, out_filenames, output_path)
            # verify that we do retrieved the correct files from comps' workitem to local
            import glob
            print(glob.glob(os.path.join(output_path, wi_id, "out", "*.*")))
            # verify we download all 8 files
            self.assertEqual(len(glob.glob(os.path.join(output_path, wi_id, "out", "*.*"))), len(out_filenames))
        finally:
            shutil.rmtree(output_path)

if __name__ == "__main__":
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='reports'))
