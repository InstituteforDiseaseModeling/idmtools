import pytest

from idmtools import IdmConfigParser
from idmtools.core.platform_factory import Platform
from idmtools_test.utils.decorators import linux_only
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence


@pytest.mark.serial
@linux_only
class TestSlurmBridge(ITestWithPersistence):
    def test_init(self):
        IdmConfigParser.clear_instance()
        IdmConfigParser(file_name="idmtools_bridged.ini")
        platform = Platform('BRIDGE')
