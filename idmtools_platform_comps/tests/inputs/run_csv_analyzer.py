# Example CSVAnalyzer for any experiment
# In this example, we will demonstrate how to use a CSVAnalyzer to analyze csv files for experiments

# First, import some necessary system and idmtools packages.
import sys

from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.analysis.csv_analyzer import CSVAnalyzer
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform


if __name__ == '__main__':

    # Set the platform where you want to run your analysis
    # In this case we are running in COMPS since the Work Item we are analyzing was run on COMPS
    platform = Platform('COMPS2')

    # Arg option for analyzer init are uid, working_dir, data in the method map (aka select_simulation_data),
    # and filenames
    # In this case, we want to provide a filename to analyze
    filenames = ['output/c.csv']
    # Initialize the analyser class with the path of the output csv file
    analyzers = [CSVAnalyzer(filenames=filenames)]

    # Set the experiment id you want to analyze
    if len(sys.argv) > 1:
        expid = [(sys.argv[1], ItemType.EXPERIMENT)]
    else:
        expid = [('9311af40-1337-ea11-a2be-f0921c167861', ItemType.EXPERIMENT)]

    # Specify the id Type, in this case an Experiment on COMPS
    manager = AnalyzeManager(partial_analyze_ok=True, ids=expid, analyzers=analyzers)
    manager.analyze()
