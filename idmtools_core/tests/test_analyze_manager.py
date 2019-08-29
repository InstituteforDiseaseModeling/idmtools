import os
import pytest

from idmtools_platform_comps.COMPSPlatform import COMPSPlatform
from idmtools.core.PlatformFactory import PlatformFactory
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.ITestWithPersistence import ITestWithPersistence
from idmtools.analysis.AnalyzeManager import AnalyzeManager
from idmtools.analysis.AddAnalyzer import AddAnalyzer

current_directory = os.path.dirname(os.path.realpath(__file__))


class TestAnalyzeManager(ITestWithPersistence):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)
        self.p = COMPSPlatform()

    def test_basic_analyzer(self):
        pass

    @pytest.skip("Do not run - this is broken")
    def test_AddAnalyzer(self):

        analyzers = [AddAnalyzer()]
        platform = PlatformFactory.create(key='COMPS')

        obj_id = '31d83b39-85b4-e911-a2bb-f0921c167866'

        obj = platform.get_object(id=obj_id, level=1)
        obj.children = platform.get_objects_by_relationship(object=obj, relationship=platform.CHILD)

        am = AnalyzeManager(configuration={}, platform=platform, items=obj.children, analyzers=analyzers)
        for a in analyzers:
            am.add_analyzer(a)
        am.analyze()
