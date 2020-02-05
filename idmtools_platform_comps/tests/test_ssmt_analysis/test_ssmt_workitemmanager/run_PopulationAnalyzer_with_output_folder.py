"""
This script is to create AnalyzerManager and do analyzer.
If you want to run it locally, just run as "python run_PopulationAnalyzer1.py expid"
If you want to run it from ssmt, you will call this file from run_ssmt_analysis.py as example
"""
import os
import sys
from sys import argv
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform

try:
    # use idmtool image
    from idmtools.analysis.analyze_manager import AnalyzeManager
except ImportError:
    # use dtk-tools image
    from simtools.Analysis.AnalyzeManager import AnalyzeManager

from analyzer.PopulationAnalyzer_with_output_folder import PopulationAnalyzer

sys.path.append(os.path.dirname(__file__))

if __name__ == "__main__":
    # Set the platform where you want to run your analysis
    # In this case we are running in COMPS SSMT
    platform = Platform('COMPS2')

    analyzers = [PopulationAnalyzer()]
    if len(sys.argv) > 1:
        expid = argv[1]
    else:
        expid = '08fc74a7-b767-e911-a2b8-f0921c167865'  # comps2 staging exp id
    am = AnalyzeManager(platform=platform, ids=[(expid, ItemType.EXPERIMENT)], analyzers=analyzers)
    am.analyze()
