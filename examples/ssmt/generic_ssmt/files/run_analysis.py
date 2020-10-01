import os
import sys
from idmtools.core import ItemType
from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.core.platform_factory import Platform

sys.path.append(os.path.dirname(__file__))
from MyAnalyzer import PopulationAnalyzer

if __name__ == "__main__":
    platform = Platform('BAYESIAN')
    analyzers = [PopulationAnalyzer()]
    exp_id = "8bb8ae8f-793c-ea11-a2be-f0921c167861"  # COMPS exp_id
    am = AnalyzeManager(ids=[(exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
    am.analyze()
