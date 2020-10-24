import unittest
import allure
import pytest
from idmtools_platform_comps.utils.singularity_build import SingularityBuildWorkItem


@pytest.mark.comps
@allure.feature("Containsers")
class TestSingularityBuild(unittest.TestCase):

    def test_docker_fetch_version_tag(self):
        sbi = SingularityBuildWorkItem()
        sbi.image_url = "docker://docker-production.packages.idmod.org/idm/dtk-ubuntu-py3.7-mpich3.3-runtime:20.04.09"