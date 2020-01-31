"""
This script is to create AnalyzerManager and do analyzer.
If you want to run it locally, just run as "python run_analysis.py expid"
If you want to run it from ssmt, you will call this file from run_ssmt_analysis.py as example
"""
import os
import sys
from sys import argv

from PopulationAnalyzer import PopulationAnalyzer
from TimeseriesAnalyzer import TimeseriesAnalyzer

try:
    # use idmtool image
    from idmtools.analysis.analyze_manager import AnalyzeManager
except ImportError:
    # use dtk-tools image
    from simtools.Analysis.AnalyzeManager import AnalyzeManager

sys.path.append(os.path.dirname(__file__))


if __name__ == "__main__":
    analyzers = [PopulationAnalyzer(), TimeseriesAnalyzer(saveOutput=True)]
    if len(sys.argv) > 1:
        expid = argv[1]
    else:
        expid = '08fc74a7-b767-e911-a2b8-f0921c167865'
    am = AnalyzeManager(exp_list=[expid], analyzers=analyzers)
    am.analyze()
