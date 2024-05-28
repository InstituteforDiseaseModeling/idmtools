# Example TagsAnalyzer for any experiment
# In this example, we will demonstrate how to use a TagsAnalyzer to put your sim tags in a csv file

# First, import some necessary system and idmtools packages.
from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.analysis.tags_analyzer import TagsAnalyzer
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform

if __name__ == '__main__':

    # Set the platform where you want to run your analysis
    # In this case we are running in COMPS since the Work Item we are analyzing was run on COMPS
    with Platform('CALCULON') as platform:

        # Arg option for analyzer init are uid, working_dir, data in the method map (aka select_simulation_data),
        # and filenames
        # Initialize the analyser class which just requires an experiment id
        analyzers = [TagsAnalyzer(output_path="output_tag")]

        # Set the experiment id you want to analyze
        experiment_id = '31285dfc-4fe6-ee11-9f02-9440c9bee941'  # comps exp id with partial succeed sims

        # Specify the id Type, in this case an Experiment on COMPS
        manager = AnalyzeManager(partial_analyze_ok=True,
                                 ids=[(experiment_id, ItemType.EXPERIMENT)],
                                 analyzers=analyzers)
        manager.analyze()
