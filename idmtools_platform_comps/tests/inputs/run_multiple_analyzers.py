"""
This script is to create AnalyzerManager and do analyzer.
If you want to run it locally, just run as "python run_analysis.py expid"
If you want to run it from ssmt, you will call this file from run_ssmt_analysis.py as example
"""
import os
import sys

from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform

from idmtools.analysis.analyze_manager import AnalyzeManager

sys.path.append(os.path.dirname(__file__))
from population_analyzer import PopulationAnalyzer  # noqa
from adult_vectors_analyzer import AdultVectorsAnalyzer  # noqa

if __name__ == "__main__":
    platform = Platform('COMPS2')
    analyzers = [PopulationAnalyzer(), AdultVectorsAnalyzer()]
    exp_id = "8bb8ae8f-793c-ea11-a2be-f0921c167861"  # COMPS2 exp_id
    am = AnalyzeManager(platform=platform, ids=[(exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
    am.analyze()
