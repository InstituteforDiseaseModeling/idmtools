import os
import sys
from sys import argv

from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.analysis.analyze_manager import AnalyzeManager

sys.path.append(os.path.dirname(__file__))
from PopulationAnalyzer import PopulationAnalyzer

if __name__ == "__main__":
    platform = Platform('SSMT')
    analyzers = [PopulationAnalyzer()]
    if len(sys.argv) >= 1:
        print(argv[1])
        expid = argv[1]
    else:
        expid = '8bb8ae8f-793c-ea11-a2be-f0921c167861'
    am = AnalyzeManager(platform=platform, ids=[(expid, ItemType.EXPERIMENT)], analyzers=analyzers)
    am.analyze()
