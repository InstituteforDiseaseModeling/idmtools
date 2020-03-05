import os
import sys

from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform

try:
    # use idmtool image
    from idmtools.analysis.analyze_manager import AnalyzeManager
except ImportError:
    # use dtk-tools image
    from simtools.Analysis.AnalyzeManager import AnalyzeManager

sys.path.append(os.path.dirname(__file__))
from MyAnalyzer import PopulationAnalyzer

if __name__ == "__main__":
    platform = Platform('COMPS2')
    analyzers = [PopulationAnalyzer()]
    exp_id = "8bb8ae8f-793c-ea11-a2be-f0921c167861" # COMPS2 exp_id
    am = AnalyzeManager(platform=platform, ids=[(exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
    am.analyze()
