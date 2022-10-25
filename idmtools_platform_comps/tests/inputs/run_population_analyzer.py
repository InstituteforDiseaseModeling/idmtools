import os
import sys

from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.analysis.analyze_manager import AnalyzeManager

sys.path.append(os.path.dirname(__file__))
from population_analyzer import PopulationAnalyzer  # noqa

if __name__ == "__main__":
    platform = Platform('BAYESIAN')
    analyzers = [PopulationAnalyzer()]

    exp_id = sys.argv[1] if len(sys.argv) > 1 else '8bb8ae8f-793c-ea11-a2be-f0921c167861'  # COMPS2 exp_id
    am = AnalyzeManager(ids=[(exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
    am.analyze()
