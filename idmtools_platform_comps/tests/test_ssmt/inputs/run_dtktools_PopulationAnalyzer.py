import os
import sys
from sys import argv

sys.path.append(os.path.dirname(__file__))

from simtools.Analysis.AnalyzeManager import AnalyzeManager
from PopulationAnalyzer import PopulationAnalyzer

if __name__ == "__main__":
    analyzers = [PopulationAnalyzer()]
    if len(sys.argv) >= 1:
        print(argv[1])
        expid = argv[1]
    else:
        expid = '8bb8ae8f-793c-ea11-a2be-f0921c167861'
    am = AnalyzeManager(exp_list=[expid], analyzers=analyzers)
    am.analyze()