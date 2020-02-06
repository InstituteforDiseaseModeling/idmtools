# Takes a demographic.json file generated from DemographicsGenerator and makes an
# InputData Request to generate climate files using the COMPS LD Workers
# Saves to output directory

import os
import json
import unittest
import pytest
import xmlrunner
import configparser

from idmtools.managers.work_item_manager import WorkItemManager
from COMPS.Data import WorkItem, WorkItemFile
from idmtools.core.platform_factory import Platform
from COMPS.Data.WorkItem import WorkerOrPluginKey
from idmtools.ssmt.ssmt_work_item import SSMTWorkItem, InputDataWorkItem

# Set up the paths
current_dir = os.path.dirname(os.path.realpath(__file__))
output_path = os.path.join(current_dir, 'output')
intermediate_dir = os.path.join(current_dir, 'intermediate', 'climate')

# # Make sure we have directory created
# if not os.path.exists(intermediate_dir): os.makedirs(intermediate_dir)
# if not os.path.exists(output_path): os.makedirs(output_path)


class InputDataWorkItemTests(unittest.TestCase):

    def setUp(self):
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        self.wi_name = "idmtools InputData WorkItem Test: Climate Files"
        self.tags = {'idmtools': self._testMethodName, 'WorkItem type': 'InputData'}
        self.p = Platform('COMPS2')
        # default_config = configparser.ConfigParser()
        # self.comps_env = default_config['COMPS2']['env']

    #------------------------------------------
    # test generate inputdata climate files with comps work item
    # create a wo.json from demo file first
    #------------------------------------------
    @pytest.mark.comps
    def test_generate_inputdata_climate_files_from_demo_file(self):
        climate_demog = os.path.join(intermediate_dir, 'Madagascar_Comoros_2.5arcmin_demographics_overlay.json')

        # do not use 'upload' for Mode. it won't generate demographic workitem
        data = {"Project": 'IDM-Madagascar', "ProjectRoot": "v2017", "Region": "",
                "IncludeNonPop": True, "Resolution": "150", "Parameters": ["tmean", "humid", "rain"], "StartYear": '2008',
                "NumYears": '1', "NaNCheck": True, "Migration": True, "Mode": 'discrete'}

        with open(climate_demog) as demo_file:
            demo = json.load(demo_file)
            if demo.get('Metadata').get('ProjectName'):
                data['Project'] = demo['Metadata']['ProjectName']

            if demo.get('Metadata').get('RegionName'):
                data['Region'] = demo['Metadata']['RegionName']

            if demo.get('Metadata').get('Resolution'):
                data['Resolution'] = str(demo['Metadata']['Resolution'])

            if demo.get('Metadata').get('IdReference'):
                data['IdReference'] = demo['Metadata']['IdReference']

            if len(self.getEntityIds(demo)) > 0:
                data['EntityIds'] = self.getEntityIds(demo)

        work_order_path = os.path.join(intermediate_dir, 'madagascar_wo.json')

        with open(work_order_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)

        inputdata_wi = InputDataWorkItem(item_name=self.wi_name, tags=self.tags)
        inputdata_wi.load_work_order(work_order_path)
        wim = WorkItemManager(inputdata_wi, self.p)
        wim.process(check_status=True)
        self.assertIsNotNone(inputdata_wi)

    def getEntityIds(self, demo):
        nlist = demo['Nodes']
        node_list = []
        for node in nlist:
            node_list.append(node['NodeID'])
        return node_list

    #------------------------------------------
    # test generate inputdata climate files with comps work item
    # use an existing wo.json to generate the climate files
    #------------------------------------------
    @pytest.mark.comps
    def test_generate_inputdata_climate_files_from_wo(self):
        work_order_path = os.path.join(intermediate_dir, 'wo.json')

        inputdata_wi = InputDataWorkItem(item_name=self.wi_name)
        inputdata_wi.load_work_order(work_order_path)
        wim = WorkItemManager(inputdata_wi, self.p)
        wim.process(check_status=True)
        self.assertIsNotNone(inputdata_wi)
