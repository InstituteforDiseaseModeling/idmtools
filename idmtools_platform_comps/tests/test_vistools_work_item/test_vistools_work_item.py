import unittest
import pytest
import xmlrunner

import os
import json

from COMPS.Data import WorkItem
from COMPS.Data.WorkItem import WorkerOrPluginKey
from idmtools.core.platform_factory import Platform
from idmtools_test import COMMON_INPUT_PATH


class VisToolsWorkItemTests(unittest.TestCase):

    def setUp(self):
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        self.wi_name = "VisTools WorkItem Test: Climate Files"
        self.tags = {'idmtools': self._testMethodName, 'WorkItem type': 'VisTools'}
        self.p = Platform('COMPS2')
        self.node_type = 'Points'

    #------------------------------------------
    # test generate inputdata climate files with comps work item
    #------------------------------------------
    @pytest.mark.skip
    @pytest.mark.comps
    # TODO: incomplete test
    # TODO: There is no work item implementation in idmtools currently... only SSMTWorkItems
    def test_vistools_work_item(self):
        # We don't have a way to create EMOD sims with demo, campaign, config, eradication.exe currently
        # So let's use an existing simulation though this will only work once (you can't pre-process multiple times)
        self.sim_id = '735e3b1d-8044-ea11-a2be-f0921c167861'

        #TODO: to replace with idmtools WorkItem implementation
        # Then create a VisTools work item to run VisTools pre-processing
        vistools_workitem = WorkItem(name='Vis-Tools Work Item',
                                     worker=WorkerOrPluginKey('VisTools', '1.0.0.0_RELEASE'),
                                     environment_name=self.p,
                                     description='pyComps: Vis-Tools preprocessing work item.')

        tags = {'SimulationId': self.sim_id}
        vistools_workitem.set_tags(tags)

        data = {"WorkItem_Type": "VisTools", "SimulationId": "" + str(self.sim_id) + "",
                "NodesRepresentation": self.node_type}

        wo_str = json.dumps(data, default=lambda obj: '')

        vistools_workitem.add_work_order(data=wo_str.encode('utf-8'))

