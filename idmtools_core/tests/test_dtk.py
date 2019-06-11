import os

from idmtools.managers import ExperimentManager
from idmtools.platforms import COMPSPlatform
from idmtools_models.dtk import DTKExperiment
from idmtools_models.dtk.defaults import DTKSIR
from tests import INPUT_PATH
from tests.utils.decorators import comps_test
from tests.utils.ITestWithPersistence import ITestWithPersistence


@comps_test
class TestDTK(ITestWithPersistence):

    def test_sir(self):
        e = DTKExperiment.from_default("test SIR", default=DTKSIR,
                                       eradication_path=os.path.join(INPUT_PATH, "dtk", "Eradication.exe"))
        sim = e.simulation()
        sim.set_parameter("Enable_Immunity", 0)
        p = COMPSPlatform()
        em = ExperimentManager(platform=p, experiment=e)
        em.run()
        em.wait_till_done()
        self.assertTrue(e.succeeded)
