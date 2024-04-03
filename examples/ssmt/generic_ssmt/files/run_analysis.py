import os
import sys
from idmtools.core import ItemType
from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.core.platform_factory import Platform

sys.path.append(os.path.dirname(__file__))
from MyAnalyzer import PopulationAnalyzer

if __name__ == "__main__":
    platform = Platform('CALCULON')
    analyzers = [PopulationAnalyzer()]
    exp_id = "b716f387-cb04-eb11-a2c7-c4346bcb1553"  # COMPS exp_id
    am = AnalyzeManager(ids=[(exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
    am.analyze()
