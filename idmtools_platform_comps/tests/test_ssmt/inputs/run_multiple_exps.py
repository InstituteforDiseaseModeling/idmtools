import os
import sys
from sys import argv

sys.path.append(os.path.dirname(__file__))

try:
    # use idmtool image
    from idmtools.analysis.analyze_manager import AnalyzeManager
except ImportError:
    # use dtk-tools image
    from simtools.Analysis.AnalyzeManager import AnalyzeManager

from PopulationAnalyzer import PopulationAnalyzer

if __name__ == "__main__":
    analyzers = [PopulationAnalyzer()]
    if len(sys.argv) > 1:
        expid = []
        expid.append(argv[1])
        expid.append(argv[2])
        print(expid)
    else:
        expid = ['8bb8ae8f-793c-ea11-a2be-f0921c167861','4ea96af7-1549-ea11-a2be-f0921c167861']
    am = AnalyzeManager(exp_list=expid, analyzers=analyzers)
    am.analyze()