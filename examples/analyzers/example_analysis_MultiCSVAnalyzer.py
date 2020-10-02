# Example CSVAnalyzer for any experiment with multiple csv outputs
# In this example, we will demonstrate how to use a CSVAnalyzer to analyze csv files for experiments

# First, import some necessary system and idmtools packages.
from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.analysis.csv_analyzer import CSVAnalyzer
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform


if __name__ == '__main__':

    # Set the platform where you want to run your analysis
    # In this case we are running in BELEGOST since the Work Item we are analyzing was run on COMPS
    platform = Platform('BELEGOST')

    # Arg option for analyzer init are uid, working_dir, data in the method map (aka select_simulation_data),
    # and filenames
    # In this case, we have multiple csv files to analyze
    filenames = ['output/a.csv', 'output/b.csv']
    # Initialize the analyser class with the path of the output csv file
    analyzers = [CSVAnalyzer(filenames=filenames, output_path="output_csv")]

    # Set the experiment id you want to analyze
    experiment_id = '1038ebdb-0904-eb11-a2c7-c4346bcb1553'  # comps exp id

    # Specify the id Type, in this case an Experiment on COMPS
    manager = AnalyzeManager(partial_analyze_ok=True, ids=[(experiment_id, ItemType.EXPERIMENT)],
                             analyzers=analyzers)
    manager.analyze()
