import sys
import os
import unittest
import xmlrunner

from idmtools.assets.file_list import FileList
from idmtools.core.platform_factory import Platform
from idmtools.managers.work_item_manager import WorkItemManager
from idmtools.ssmt.idm_work_item import SSMTWorkItem
from COMPS.Data.WorkItem import WorkItem, RelationType
from COMPS.Data import QueryCriteria, AssetCollection
from COMPS.Client import Client
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence

current_directory = os.path.dirname(os.path.realpath(__file__))
outdir_path = os.path.join(current_directory, 'climate')


class ClimateGenerationTest(ITestWithPersistence):

    @classmethod
    def setUpClass(cls):
        cls.current_directory = current_directory
        # Create a config builder from set of input files
        input_dir = os.path.dirname(os.path.abspath(__file__))
        print(input_dir)

    def setUp(self):
        print(self._testMethodName)
        self.wi_name = 'idmtools: ERA5 weather generation'

    # @classmethod
    # # delete workitem after test is done
    # def tearDown(self):
    #     try:
    #
    #         wi = WorkItem.get(self.workitem_id)
    #     except:
    #         wi = None
    #     wi.delete()
    #
    #     try:
    #         WorkItem.get(wi.id)
    #     except RuntimeError as e:
    #         pass

    #------------------------------------------
    # test generate ERA5 climate files
    #------------------------------------------
    def test_generate_era5_climate_files(self):
        wi_name = 'idmtools: ERA5 weather generation'

        # A .csv or a demographics file containing input coordinates
        path_to_points_file = outdir_path
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
        user_files = FileList(root=path_to_points_file, files_in_root=[points_file])

        platform = Platform('COMPS2')
        wi = SSMTWorkItem(item_name=self.wi_name, docker_image=docker_image, command=command, user_files=user_files,
                          tags={'dtktools': self._testMethodName, 'WorkItem type': 'Docker', 'Command': command})
        wim = WorkItemManager(wi, platform)
        wim.process(check_status=True)

        # Get the work item, related asset collection, and assets
        wi_id = wi.uid
        print(wi_id)

        workitem = WorkItem.get(wi_id)
        acs = workitem.get_related_asset_collections(RelationType.Created)

        for ac in acs:
            print(ac.id)
            created_ac = str(ac.id)

            # Retrieve climate files from AC and save to local disk
            ac = AssetCollection.get(created_ac)
            ac.refresh(QueryCriteria().select_children('assets'))

            for acf in ac.assets:
                # write them to climate dir to use to run DTK test
                fn = os.path.join(outdir_path, acf.file_name)
                print('   Writing ' + fn)

                with open(fn, 'wb') as outfile:
                    outfile.write(acf.retrieve())

        self.validate(wi)

    #------------------------------------------
    # test getting the climate files and saving them local for the DTK run test
    #------------------------------------------
    # def test_retrieve_climate_files(self, wim):
    #     # Get workitem
    #     self.workitem_id = wi.uid
    #     wi = WorkItem.get(wi.uid)
    #     print("workitem id :" + str(wi.id))
    #
    #     # Get the created ac written to file
    #     ac_file = open("ac_file.txt", "r")
    #     created_ac = ac_file.read()
    #     print("AC:" + created_ac)
    #
    #     # Retrieve climate files from AC and save to local disk
    #     ac = AssetCollection.get(created_ac)
    #     ac.refresh(QueryCriteria().select_children('assets'))
    #
    #     for acf in ac.assets:
    #         # write them to Assets dir
    #         fn = os.path.join(outdir_path, acf.file_name)
    #         print('   Writing ' + fn)
    #
    #         with open(fn, 'wb') as outfile:
    #             outfile.write(acf.retrieve())
    #
    #     self.validate(wi)

    # ------------------------------------------
    # validate results from the work item
    # ------------------------------------------
    def validate(self, wi, output_path=None):
        # Get workitem
        self.workitem_id = wi.uid
        wi = WorkItem.get(wi.uid)
        print("workitem id :" + str(wi.id))

        # File paths of climate files we want to get
        paths = [
            'out/dtk_15arcmin_air_temperature_daily.bin',
            'out/dtk_15arcmin_air_temperature_daily.bin.json',
            'out/dtk_15arcmin_land_temperature_daily.bin',
            'out/dtk_15arcmin_land_temperature_daily.bin.json',
            'out/dtk_15arcmin_rainfall_daily.bin',
            'out/dtk_15arcmin_rainfall_daily.bin.json',
            'out/dtk_15arcmin_relative_humidity_daily.bin',
            'out/dtk_15arcmin_relative_humidity_daily.bin.json'
        ]

        # retrieve climate files from Output dir of workitem to validate they were generated
        if output_path is None:
            barr_out = wi.retrieve_output_file_info(paths)
        else:  # if output has folder, retrieve from there
            barr_out = wi.retrieve_output_file_info([os.path.join('out', paths)])

        print(barr_out)


if __name__ == "__main__":
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='reports'))
