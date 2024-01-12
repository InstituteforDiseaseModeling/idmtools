import os
import sys
from sys import argv
from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform

sys.path.append(os.path.dirname(__file__))
from population_analyzer import PopulationAnalyzer  # noqa

if __name__ == "__main__":
    platform = Platform('cumulus')

    analyzers = [PopulationAnalyzer()]
    if len(sys.argv) > 1:
        expid = []
        expid.append((argv[1], ItemType.EXPERIMENT))
        expid.append((argv[2], ItemType.EXPERIMENT))
    else:
        expid = [('8bb8ae8f-793c-ea11-a2be-f0921c167861', ItemType.EXPERIMENT),
                 ('4ea96af7-1549-ea11-a2be-f0921c167861', ItemType.EXPERIMENT)]
    am = AnalyzeManager(ids=expid, analyzers=analyzers)
    am.analyze()
