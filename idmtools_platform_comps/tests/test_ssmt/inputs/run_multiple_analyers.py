"""
This script is to create AnalyzerManager and do analyzer.
If you want to run it locally, just run as "python run_analysis.py expid"
If you want to run it from ssmt, you will call this file from run_ssmt_analysis.py as example
"""
import os
import sys
from sys import argv

sys.path.append(os.path.dirname(__file__))

from simtools.Analysis.AnalyzeManager import AnalyzeManager
from PopulationAnalyzer import PopulationAnalyzer
from AdultVectorsAnalyzer import AdultVectorsAnalyzer

if __name__ == "__main__":
    analyzers = [PopulationAnalyzer(), AdultVectorsAnalyzer()]
    if len(sys.argv) > 1:
        expid = argv[1]
    else:
        expid = '8bb8ae8f-793c-ea11-a2be-f0921c167861'
    am = AnalyzeManager(exp_list=[expid], analyzers=analyzers)
    am.analyze()