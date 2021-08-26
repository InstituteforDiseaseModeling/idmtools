import allure
import ast
import json
import os
import unittest
import pytest
from idmtools.assets import AssetCollection, Asset
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools_platform_comps.ssmt_work_items.comps_workitems import VisToolsWorkItem
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.utils import del_folder, get_case_name

DEFAULT_INPUT_PATH = os.path.join(COMMON_INPUT_PATH, "malaria_brazil_central_west_spatial")
DEFAULT_ERADICATION_PATH = os.path.join(DEFAULT_INPUT_PATH, "Assets", "Eradication.exe")
DEFAULT_CONFIG_PATH = os.path.join(DEFAULT_INPUT_PATH, "config.json")
DEFAULT_CAMPAIGN_PATH = os.path.join(DEFAULT_INPUT_PATH, "campaign.json")


def param_update(simulation, param, value):
    return simulation.set_parameter(param, value)


@pytest.mark.comps
@pytest.mark.long
@allure.story("COMPS")
@allure.story("SSMT")
@allure.suite("idmtools_platform_comps")
class TestVisToolsWorkItem(unittest.TestCase):

    def generate_sim(self):
        command = "Assets/Eradication.exe --config config.json --input-path ./Assets"
        task = CommandTask(command=command)

        # add Eradication.exe to Assets dir in comps
        # ast = Asset(absolute_path=DEFAULT_ERADICATION_PATH)
        # task.common_assets.add_asset(ast)  #

        # add eradication.exe to current dir in comps
        eradication_asset = Asset(absolute_path=DEFAULT_ERADICATION_PATH)
        task.transient_assets.add_asset(eradication_asset)

        # add config.json to current dir in comps
        config_asset = Asset(absolute_path=DEFAULT_CONFIG_PATH)
        task.transient_assets.add_asset(config_asset)

        # add campaign.json to current dir in comps
        campaign_asset = Asset(absolute_path=DEFAULT_CAMPAIGN_PATH)
        task.transient_assets.add_asset(campaign_asset)

        # add all files from local dir to assetcollection
        assets_path = os.path.join(DEFAULT_INPUT_PATH, "Assets")
        ac = AssetCollection.from_directory(assets_directory=assets_path)

        # create experiment from task
        experiment = Experiment.from_task(task, name="test_vistools_work_item.py--experiment", assets=ac)
        experiment.run(wait_until_done=True)

        # return first simulation
        simulations = self.platform.get_children(experiment.uid, ItemType.EXPERIMENT, force=True)
        return simulations

    @classmethod
    def setUpClass(cls):
        cls.platform = Platform('COMPS2')
        cls.sim_id = str(cls.generate_sim(cls)[0].uid)
        node_type = 'Points'
        data = {"SimulationId": "" + cls.sim_id + "", "NodesRepresentation": node_type}
        tags = {'idmtools': "vistool test", 'WorkItem type': 'VisTools', 'SimulationId': cls.sim_id}
        cls.wi = VisToolsWorkItem(name="test_vistools_work_item.py", tags=tags, work_order=data, related_simulations=[cls.sim_id])
        cls.wi.run(wait_on_done=True)

    def setUp(self):
        self.case_name = get_case_name(os.path.basename(__file__) + "--" + self._testMethodName)

    # ------------------------------------------
    # test vistools workitem and outpur
    # ------------------------------------------
    def test_vistools_work_item_and_output(self):
        print(self.case_name)

        # validate output in workitem
        output_path = "output_workitem"
        del_folder(output_path)

        out_filenames = ["WorkOrder.json"]
        ret = self.platform.get_files_by_id(self.wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, output_path)
        temp = ret["WorkOrder.json"]
        temp_dict = ast.literal_eval(temp.decode('utf-8'))
        self.assertEqual(temp_dict["WorkItem_Type"], "VisTools")
        self.assertEqual(temp_dict["SimulationId"], self.sim_id)
        self.assertEqual(temp_dict["NodesRepresentation"], "Points")

        # validate file get download to local
        self.assertTrue(os.path.exists(os.path.join(output_path, str(self.wi.uid), "WorkOrder.json")))

        # Validate another way to retriever workitem output
        ret = self.platform.get_files(self.wi, out_filenames)
        temp = ret["WorkOrder.json"]
        temp_dict = ast.literal_eval(temp.decode('utf-8'))
        # temp_dict = json.loads(temp[0].decode('utf-8'))
        self.assertEqual(temp_dict["WorkItem_Type"], "VisTools")
        self.assertEqual(temp_dict["SimulationId"], self.sim_id)
        self.assertEqual(temp_dict["NodesRepresentation"], "Points")

    def test_vistools_output_in_simulation(self):
        print(self.case_name)
        # get comps's simulation object
        sim = self.platform.get_item(self.sim_id, item_type=ItemType.SIMULATION, raw=True)

        # get Vis-Tools dynamic folder in simulation output  which is Vis-Tools/md5.
        # to get this md5 info, we need to call:
        # retrieve_output_file_info which only existing in pycomps
        metadata = sim.retrieve_output_file_info([])
        friendly_name_list = []
        for i in list(metadata):
            if "Vis-Tools" in i.path_from_root:
                friendly_name_list.append(i.friendly_name)
                p = i.path_from_root  # p should have path :"Vis-Tools/md5"

        # --------------------------------------------------------------------------
        # Verify total files under Vis-Tools\md5 dir
        # --------------------------------------------------------------------------
        self.assertTrue(len(friendly_name_list) == 10)
        friendly_name_list.sort()
        for index, item in enumerate(friendly_name_list, start=0):
            print(index, item)
        self.assertTrue(friendly_name_list[8] == 'visset.json')
        self.assertTrue(friendly_name_list[0] == 'VtAssetMap.json')
        self.assertTrue(friendly_name_list[1] == 'VtRunInfo.json')
        self.assertTrue(friendly_name_list[2] == 'VtWorkerIntegrateStdErr.txt')
        self.assertTrue(friendly_name_list[3] == 'VtWorkerIntegrateStdOut.txt')
        self.assertTrue(friendly_name_list[4] == 'VtWorkerPrepStdErr.txt')
        self.assertTrue(friendly_name_list[5] == 'VtWorkerPrepStdOut.txt')
        self.assertTrue(friendly_name_list[6] == 'VtWorkerSurveyStdErr.txt')
        self.assertTrue(friendly_name_list[7] == 'VtWorkerSurveyStdOut.txt')
        self.assertTrue(friendly_name_list[9] == 'vt_preprocess.py')

        # --------------------------------------------------------------------------
        # Verify visset.json content
        # --------------------------------------------------------------------------
        output_path = "output_simulation"
        del_folder(output_path)
        out_filenames = [p + "/visset.json"]
        result = self.platform.get_files_by_id(self.sim_id, ItemType.SIMULATION, out_filenames, output_path)
        # validate file visset.json  get download to local
        self.assertTrue(os.path.exists(os.path.join(output_path, str(self.sim_id), p, "visset.json")))

        # decoding the JSON string to dictionary
        d = json.loads(result[p + "/visset.json"].decode('utf-8'))

        # Testcase2: Validate all fields in visset.json file:
        visset_name = d["name"]
        self.assertEqual(d["timestepCount"], 4380)
        self.assertEqual(d["targetClient"], 'Geospatial')
        self.assertEqual(d["version"], '1.2')
        #self.assertEqual(d["startDate"], (date.today() - timedelta(d["timestepCount"])).isoformat())
        self.assertEqual(d["options"]["defaultBaseLayer"], 'Bing Maps Aerial')
        self.assertEqual(d["options"]["clockStepDurationSecs"], 14400)
        self.assertEqual(d["options"]["clockInitialTimestep"], 0)
        self.assertEqual(d["options"]["clockAutoRun"], False)
        self.assertEqual(d["options"]["clockAnimFrameSecs"], 14400)
        self.assertEqual(d["options"]["clockArrowAdvance"], 14400)
        self.assertEqual(d["options"]["clockShiftArrowAdvance"], 86400)

        # Varify this sim use Points type which defined in workOrder
        self.assertEqual(d["options"]["nodeVis"]["visType"], "Points")

        # Varify pointOptions default values
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointColor"]["friendlyName"], "Color")
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointColor"]["desc"],
                         "Node point fill color")
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointColor"]["returnDesc"],
                         "String containing color, e.g. '#101080' or 'red'")
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointColor"]["returnType"], "string")
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointColor"]["returnConversion"],
                         "CesiumNodes.stringToCesiumColor")
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointColor"]["source"], None)
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointColor"]["function"], None)
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointColor"]["defaultFunction"],
                         "sampleGradient()")
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointOpacity"]["friendlyName"], "Opacity")
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointOpacity"]["desc"],
                         "Node point opacity, [0, 1]")
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointOpacity"]["returnDesc"], "Float")
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointOpacity"]["returnType"], "number")
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointOpacity"]["returnConversion"], None)
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointOpacity"]["source"], None)
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointOpacity"]["function"], None)
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointOpacity"]["defaultFunction"], None)

        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointOutlineColor"]["friendlyName"],
                         "Outline color")
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointOutlineColor"]["desc"],
                         "Node point outline color")
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointOutlineColor"]["returnDesc"],
                         "String containing color, e.g. '#101080' or 'red'")
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointOutlineColor"]["returnType"], "string")
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointOutlineColor"]["returnConversion"],
                         "CesiumNodes.stringToCesiumColor")
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointOutlineColor"]["source"], None)
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointOutlineColor"]["function"], None)
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointOutlineColor"]["defaultFunction"],
                         "sampleGradient()")
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointOutlineThickness"]["friendlyName"],
                         "Outline thickness")
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointOutlineThickness"]["desc"],
                         "Node point outline thickness in pixels")
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointOutlineThickness"]["returnDesc"],
                         "Float")
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointOutlineThickness"]["returnType"],
                         "number")
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointOutlineThickness"]["returnConversion"],
                         None)
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointOutlineThickness"]["source"], None)
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointOutlineThickness"]["function"], None)
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["sinks"]["pointOutlineThickness"]["defaultFunction"],
                         None)

        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["show"], True)
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["gradient"], "YlOrRd")
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["gradientRangeLow"], 0)
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["gradientRangeHigh"], 1)
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["scale"], 1.0)
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["defaultColor"], "#ffff00")
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["defaultOpacity"], 1.0)
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["defaultOutlineColor"], "rgba(0,0,0,0)")
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["defaultOutlineThicknessPx"], 0)
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["defaultSizePx"], 6)
        self.assertEqual(d["options"]["nodeVis"]["pointOptions"]["selectionIndicatorColor"], "#00ff00")

        # Varify shapeOptions default values
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeColor"]["friendlyName"], "Color")
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeColor"]["desc"],
                         "Node shape fill color")
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeColor"]["returnDesc"],
                         "String containing color, e.g. '#101080' or 'red'")
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeColor"]["returnType"], "string")
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeColor"]["returnConversion"],
                         "CesiumNodes.stringToCesiumColor")
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeColor"]["source"], None)
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeColor"]["function"], None)
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeColor"]["defaultFunction"],
                         "sampleGradient()")
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeOpacity"]["friendlyName"], "Opacity")
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeOpacity"]["desc"],
                         "Node shape opacity, [0, 1]")
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeOpacity"]["returnDesc"], "Float")
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeOpacity"]["returnType"], "number")
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeOpacity"]["returnConversion"], None)
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeOpacity"]["source"], None)
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeOpacity"]["function"], None)
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeOpacity"]["defaultFunction"], None)
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeSize"]["friendlyName"], "Size")
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeSize"]["desc"], "Node size in meters")
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeSize"]["returnDesc"], "Float")
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeSize"]["returnType"], "number")
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeSize"]["returnConversion"], None)
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeSize"]["source"], None)
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeSize"]["function"], None)
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeSize"]["defaultFunction"], None)
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeExtrusion"]["friendlyName"],
                         "Extrusion")
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeExtrusion"]["desc"],
                         "Node extrusion from surface in meters")
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeExtrusion"]["returnDesc"], "Float")
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeExtrusion"]["returnType"], "number")
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeExtrusion"]["returnConversion"], None)
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeExtrusion"]["source"], None)
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeExtrusion"]["function"], None)
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["sinks"]["shapeExtrusion"]["defaultFunction"], None)
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["show"], True)
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["gradient"], "YlOrRd")
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["gradientRangeLow"], 0)
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["gradientRangeHigh"], 1)
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["scale"], 1.0)
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["defaultColor"], "#ffff00")
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["defaultOpacity"], 1.0)
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["defaultShape"], "Square")
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["defaultSizeM"], 100)
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["defaultExtrusionM"], 1)
        self.assertEqual(d["options"]["nodeVis"]["shapeOptions"]["selectionIndicatorColor"], "#00ff00")

        self.assertEqual(d["options"]["nodeInsets"]["spatialChannels"], "all")
        self.assertEqual(d["options"]["nodeInsets"]["traceColor"], "#ffff00")
        self.assertEqual(d["options"]["nodeInsets"]["timeBarColor"], "#00ff00")

        self.assertEqual(d["options"]["heatmapVis"]["sinks"]["source"]["friendlyName"], "Heatmap")
        self.assertEqual(d["options"]["heatmapVis"]["sinks"]["source"]["desc"], "Heatmap")
        self.assertEqual(d["options"]["heatmapVis"]["sinks"]["source"]["returnDesc"], "Float")
        self.assertEqual(d["options"]["heatmapVis"]["sinks"]["source"]["returnType"], "number")
        self.assertEqual(d["options"]["heatmapVis"]["sinks"]["source"]["returnConversion"], None)
        self.assertEqual(d["options"]["heatmapVis"]["sinks"]["source"]["source"], None)
        self.assertEqual(d["options"]["heatmapVis"]["sinks"]["source"]["function"], None)
        self.assertEqual(d["options"]["heatmapVis"]["show"], False)
        self.assertEqual(d["options"]["heatmapVis"]["gradient"], "YlGnBu")
        self.assertEqual(d["options"]["heatmapVis"]["gradientRangeLow"], 0)
        self.assertEqual(d["options"]["heatmapVis"]["gradientRangeHigh"], 1)
        self.assertEqual(d["options"]["heatmapVis"]["opacity"], 1.0)
        self.assertEqual(d["options"]["heatmapVis"]["sizePx"], 1024)

        self.assertEqual(d["options"]["markersVis"], {})
        self.assertEqual(d["options"]["migrationsVis"]["maxSimultaneousMigrations"], 0)

        # Varify InsetChart panel default values
        self.assertEqual(d["options"]["insetCharts"]["show"], True)
        self.assertEqual(d["options"]["insetCharts"]["defaultChannelName"], "Prevalence")
        self.assertEqual(d["options"]["insetCharts"]["traceColor"], "#ffff00")
        self.assertEqual(d["options"]["insetCharts"]["timeBarColor"], "#00ff00")
        self.assertEqual(d["options"]["insetCharts"]["location"], "BC")
        self.assertEqual(d["options"]["insetCharts"]["width"], "25%")
        self.assertEqual(d["options"]["insetCharts"]["height"], "33%")

        # Verify total 4 spatial reports
        self.assertEqual(len(d["links"]["spatial"]), 4)

        # Verify SpatialReport_Adult_Vectors detail
        self.assertEqual(d["links"]["spatial"]["SpatialReport_Adult_Vectors"]["url"],
                         "/" + visset_name + "/output/SpatialReport_Adult_Vectors.bin")
        self.assertEqual(d["links"]["spatial"]["SpatialReport_Adult_Vectors"]["show"], True)
        self.assertEqual(d["links"]["spatial"]["SpatialReport_Adult_Vectors"]["friendlyName"], "Adult Vectors")
        self.assertGreater(d["links"]["spatial"]["SpatialReport_Adult_Vectors"]["min"], 8.0)
        self.assertLess(d["links"]["spatial"]["SpatialReport_Adult_Vectors"]["max"], 22010316.0)
        self.assertTrue(str(d["links"]["spatial"]["SpatialReport_Adult_Vectors"]["url_asset"]).endswith(
            "/SpatialReport_Adult_Vectors.bin"))

        # Verify SpatialReport_Daily_EIR detail
        self.assertEqual(d["links"]["spatial"]["SpatialReport_Daily_EIR"]["url"],
                         "/" + visset_name + "/output/SpatialReport_Daily_EIR.bin")
        self.assertEqual(d["links"]["spatial"]["SpatialReport_Daily_EIR"]["show"], True)
        self.assertEqual(d["links"]["spatial"]["SpatialReport_Daily_EIR"]["friendlyName"], "Daily EIR")
        self.assertEqual(d["links"]["spatial"]["SpatialReport_Daily_EIR"]["min"], 0.0)
        self.assertLess(d["links"]["spatial"]["SpatialReport_Daily_EIR"]["max"], 19758.142578125)
        self.assertTrue(str(d["links"]["spatial"]["SpatialReport_Daily_EIR"]["url_asset"]).endswith(
            "/SpatialReport_Daily_EIR.bin"))

        # Verify SpatialReport_Population detail
        self.assertEqual(d["links"]["spatial"]["SpatialReport_Population"]["url"],
                         "/" + visset_name + "/output/SpatialReport_Population.bin")
        self.assertEqual(d["links"]["spatial"]["SpatialReport_Population"]["show"], True)
        self.assertEqual(d["links"]["spatial"]["SpatialReport_Population"]["friendlyName"], "Population")
        self.assertGreater(d["links"]["spatial"]["SpatialReport_Population"]["min"], 5.0)
        self.assertLess(d["links"]["spatial"]["SpatialReport_Population"]["max"], 566.22650146484375)
        self.assertTrue(str(d["links"]["spatial"]["SpatialReport_Population"]["url_asset"]).endswith(
            "/SpatialReport_Population.bin"))

        # Verify SpatialReport_Prevalence detail
        self.assertEqual(d["links"]["spatial"]["SpatialReport_Prevalence"]["url"],
                         "/" + visset_name + "/output/SpatialReport_Prevalence.bin")
        self.assertEqual(d["links"]["spatial"]["SpatialReport_Prevalence"]["show"], True)
        self.assertEqual(d["links"]["spatial"]["SpatialReport_Prevalence"]["friendlyName"], "Prevalence")
        self.assertEqual(d["links"]["spatial"]["SpatialReport_Prevalence"]["min"], 0.0)
        self.assertEqual(d["links"]["spatial"]["SpatialReport_Prevalence"]["max"], 1.0)
        self.assertTrue(str(d["links"]["spatial"]["SpatialReport_Prevalence"]["url_asset"]).endswith(
            "/SpatialReport_Prevalence.bin"))

        # Varify InsetChart
        self.assertEqual(d["links"]["czml"], {})
        self.assertEqual(d["links"]["inset"]["url"], "/" + visset_name + "/output/InsetChart.json")
        self.assertTrue(str(d["links"]["inset"]["url_asset"]).__contains__("/InsetChart.json"))
        self.assertEqual(d["links"]["customBaseLayer"], None)

        # Only random check few nodes
        self.assertEqual(d["nodes"][0]['nodeId'], 207685437)
        self.assertEqual(d["nodes"][0]['longitude'], -47.93750000000001)
        self.assertEqual(d["nodes"][0]['latitude'], -12.812500000000009)
        self.assertEqual(d["nodes"][0]['altitude'], 253.919998168945)
        self.assertEqual(d["nodes"][0]['InitialPopulation'], 17)

        self.assertEqual(d["nodes"][1]['nodeId'], 207685443)
        self.assertEqual(d["nodes"][1]['longitude'], -47.93750000000001)
        self.assertEqual(d["nodes"][1]['latitude'], -12.562500000000009)
        self.assertEqual(d["nodes"][1]['altitude'], 253.919998168945)
        self.assertEqual(d["nodes"][1]['InitialPopulation'], 17)

        # Varify total 36 nodes
        self.assertEqual(len(d["nodes"]), 36)

        # Verify sim id
        self.assertEqual(d["simId"], str(self.sim_id))

        # --------------------------------------------------------------------------
        # Verify VtAssetMap.json details
        # --------------------------------------------------------------------------
        # Get VtAssetMap.json bytes array in memory
        vtassetmap = sim.retrieve_output_files([p + '/VtAssetMap.json'])

        # decoding to dictionary
        vtassetmap_dic = json.loads(vtassetmap[0].decode('utf-8'))
        self.assertTrue(len(vtassetmap_dic) == 20)

        self.assertTrue(
            str(vtassetmap_dic['/' + visset_name + '/output/BinnedReport.json']).endswith('/BinnedReport.json'))
        self.assertTrue(str(vtassetmap_dic['/' + visset_name + '/output/SpatialReport_Adult_Vectors.bin']).endswith(
            '/SpatialReport_Adult_Vectors.bin'))
        self.assertTrue(str(vtassetmap_dic['/' + visset_name + '/output/SpatialReport_Daily_EIR.bin']).endswith(
            '/SpatialReport_Daily_EIR.bin'))
        self.assertTrue(str(vtassetmap_dic['/' + visset_name + '/output/DemographicsSummary.json']).endswith(
            '/DemographicsSummary.json'))
        self.assertTrue(str(vtassetmap_dic['/' + visset_name + '/output/InsetChart.json']).endswith('/InsetChart.json'))
        self.assertTrue(str(vtassetmap_dic['/' + visset_name + '/output/SpatialReport_Population.bin']).endswith(
            '/SpatialReport_Population.bin'))
        self.assertTrue(str(vtassetmap_dic['/' + visset_name + '/output/SpatialReport_Prevalence.bin']).endswith(
            '/SpatialReport_Prevalence.bin'))
        self.assertTrue(str(vtassetmap_dic['/' + visset_name + '/output/VectorSpeciesReport.json']).endswith(
            '/VectorSpeciesReport.json'))
        self.assertTrue(str(vtassetmap_dic['/' + visset_name + '/campaign.json']).endswith('/campaign.json'))
        self.assertTrue(str(vtassetmap_dic['/' + visset_name + '/config.json']).endswith('/config.json'))
        self.assertTrue(str(vtassetmap_dic['/' + visset_name + '/status.txt']).endswith('/status.txt'))
        self.assertTrue(str(vtassetmap_dic['/' + visset_name + '/stderr.txt']).endswith('/stderr.txt'))
        self.assertTrue(str(vtassetmap_dic['/' + visset_name + '/stdout.txt']).endswith('/stdout.txt'))
        self.assertTrue(str(vtassetmap_dic['/' + visset_name + '/' + p + '/visset.json']).endswith('/visset.json'))
        self.assertTrue(str(vtassetmap_dic['/' + visset_name + '/' + p + '/VtWorkerPrepStdErr.txt']).endswith(
            '/VtWorkerPrepStdErr.txt'))
        self.assertTrue(str(vtassetmap_dic['/' + visset_name + '/' + p + '/VtWorkerPrepStdOut.txt']).endswith(
            '/VtWorkerPrepStdOut.txt'))
        self.assertTrue(str(vtassetmap_dic['/' + visset_name + '/' + p + '/VtWorkerSurveyStdErr.txt']).endswith(
            '/VtWorkerSurveyStdErr.txt'))
        self.assertTrue(str(vtassetmap_dic['/' + visset_name + '/' + p + '/VtWorkerSurveyStdOut.txt']).endswith(
            '/VtWorkerSurveyStdOut.txt'))
        self.assertTrue(
            str(vtassetmap_dic['/' + visset_name + '/' + p + '/vt_preprocess.py']).endswith('/vt_preprocess.py'))

        # Validate download the urls are actully working
        import requests

        response = requests.get(vtassetmap_dic['/' + visset_name + '/output/BinnedReport.json'])
        # assert response.status_code < 400
        self.assertTrue(response.status_code < 400)

        response = requests.get(vtassetmap_dic['/' + visset_name + '/output/SpatialReport_Adult_Vectors.bin'])
        self.assertTrue(response.status_code < 400)

        response = requests.get(vtassetmap_dic['/' + visset_name + '/output/SpatialReport_Daily_EIR.bin'])
        self.assertTrue(response.status_code < 400)

        response = requests.get(vtassetmap_dic['/' + visset_name + '/output/DemographicsSummary.json'])
        self.assertTrue(response.status_code < 400)

        response = requests.get(vtassetmap_dic['/' + visset_name + '/output/InsetChart.json'])
        self.assertTrue(response.status_code < 400)

        response = requests.get(vtassetmap_dic['/' + visset_name + '/output/SpatialReport_Population.bin'])
        self.assertTrue(response.status_code < 400)

        response = requests.get(vtassetmap_dic['/' + visset_name + '/output/SpatialReport_Prevalence.bin'])
        self.assertTrue(response.status_code < 400)

        response = requests.get(vtassetmap_dic['/' + visset_name + '/output/VectorSpeciesReport.json'])
        self.assertTrue(response.status_code < 400)

        response = requests.get(vtassetmap_dic['/' + visset_name + '/campaign.json'])
        self.assertTrue(response.status_code < 400)

        response = requests.get(vtassetmap_dic['/' + visset_name + '/config.json'])
        self.assertTrue(response.status_code < 400)

        response = requests.get(vtassetmap_dic['/' + visset_name + '/status.txt'])
        self.assertTrue(response.status_code < 400)

        response = requests.get(vtassetmap_dic['/' + visset_name + '/stderr.txt'])
        self.assertTrue(response.status_code < 400)

        response = requests.get(vtassetmap_dic['/' + visset_name + '/stdout.txt'])
        self.assertTrue(response.status_code < 400)

        response = requests.get(vtassetmap_dic['/' + visset_name + '/' + p + '/visset.json'])
        self.assertTrue(response.status_code < 400)

        response = requests.get(vtassetmap_dic['/' + visset_name + '/' + p + '/VtWorkerPrepStdErr.txt'])
        self.assertTrue(response.status_code < 400)

        response = requests.get(vtassetmap_dic['/' + visset_name + '/' + p + '/VtWorkerPrepStdOut.txt'])
        self.assertTrue(response.status_code < 400)

        response = requests.get(vtassetmap_dic['/' + visset_name + '/' + p + '/VtWorkerSurveyStdErr.txt'])
        self.assertTrue(response.status_code < 400)

        response = requests.get(vtassetmap_dic['/' + visset_name + '/' + p + '/VtWorkerSurveyStdOut.txt'])
        self.assertTrue(response.status_code < 400)

        response = requests.get(vtassetmap_dic['/' + visset_name + '/' + p + '/vt_preprocess.py'])
        self.assertTrue(response.status_code < 400)

    # def generate_sim(self):
    #     Old way to create EMODExpierment
    #     self.case_name = os.path.basename(__file__)
    #     assets_path = os.path.join(DEFAULT_INPUT_PATH, "Assets")
    #     ac = AssetCollection.from_directory(assets_directory=assets_path)
    #     e = EMODExperiment.from_files(name=self.case_name,
    #                                   eradication_path=DEFAULT_ERADICATION_PATH,
    #                                   config_path=DEFAULT_CONFIG_PATH,
    #                                   campaign_path=DEFAULT_CAMPAIGN_JSON,
    #                                   demographics_paths=DEFAULT_DEMOGRAPHICS_JSON)
    #     e.legacy_exe = True
    #     e.add_assets(ac)
    #
    #     builder = ExperimentBuilder()
    #     set_Run_Number = partial(param_update, param="Run_Number")
    #     builder.add_sweep_definition(set_Run_Number, range(1))
    #     e.add_builder(builder)
    #     em = ExperimentManager(experiment=e, platform=self.p)
    #     em.run()
    #     em.wait_till_done()
    #     simulations = self.p.get_children(em.experiment.uid, ItemType.EXPERIMENT, force=True)
    #     return simulations
