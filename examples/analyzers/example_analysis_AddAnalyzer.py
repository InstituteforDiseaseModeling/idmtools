# Example AddAnalyzer for EMOD Experiment
# In this example, we will demonstrate how to create an AddAnalyzer to analyze an experiment's output file

# First, import some necessary system and idmtools packages.
from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.analysis.add_analyzer import AddAnalyzer
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform

if __name__ == '__main__':

    # Set the platform where you want to run your analysis
    # In this case we are running in BELEGOST, but this can be changed to run 'CALCULON'
    with Platform('BELEGOST') as platform:

        # Arg option for analyzer init are uid, working_dir, data in the method map (aka select_simulation_data),
        # and filenames
        # In this case, we want to provide a filename to analyze
        filenames = ['StdOut.txt']
        # Initialize the analyser class with the name of file to save to and start the analysis
        analyzers = [AddAnalyzer(filenames=filenames)]

        # Set the experiment you want to analyze
        experiment_id = '6f305619-64b3-ea11-a2c6-c4346bcb1557'  # comps exp id

        # Specify the id Type, in this case an Experiment
        manager = AnalyzeManager(ids=[(experiment_id, ItemType.EXPERIMENT)], analyzers=analyzers)
        manager.analyze()
