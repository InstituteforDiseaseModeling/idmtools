import os
import sys

from MyAnalyzer import PopulationAnalyzer

try:
    # use idmtool image
    from idmtools.analysis.analyze_manager import AnalyzeManager
except ImportError:
    # use dtk-tools image
    from simtools.Analysis.AnalyzeManager import AnalyzeManager



sys.path.append(os.path.dirname(__file__))

if __name__ == "__main__":
    analyzers = [PopulationAnalyzer()]
    am = AnalyzeManager(exp_list=["8bb8ae8f-793c-ea11-a2be-f0921c167861"], analyzers=analyzers)
    am.analyze()
