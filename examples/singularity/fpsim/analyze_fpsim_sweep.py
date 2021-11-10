from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.analysis.download_analyzer import DownloadAnalyzer
from idmtools.analysis.csv_analyzer import CSVAnalyzer
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform

if __name__ == '__main__':

    # First, load the experiment id from the run_sim_sweep.id file
    with open('run_sim_sweep.id','r') as infile:
        contents = infile.read()
        split_contents = contents.split(':')
        sweep_experiment_id = split_contents[0]

    # Set the platform where you want to run your analysis
    # In this case we are running in BELEGOST, but this can be changed to run 'Local'
    with Platform('CALCULON') as platform:

        # Arg option for analyzer init are uid, working_dir, data in the method map (aka select_simulation_data),
        # and filenames
        # In this case, we want to provide a filename to analyze
        filenames = ['StdOut.txt','InsetChart.csv']
        # Initialize the analyser class with the path of the output files to download
        csv_data = CSVAnalyzer(filenames=['InsetChart.csv'], output_path='download_csv')
        std_outs = DownloadAnalyzer(filenames=filenames, output_path='download')
        analyzers = [csv_data, std_outs]

        # Set the experiment you want to analyze
        experiment_id = sweep_experiment_id  # comps exp id

        # Specify the id Type, in this case an Experiment
        manager = AnalyzeManager(ids=[(experiment_id, ItemType.EXPERIMENT)],
                                 analyzers=analyzers)
        manager.analyze()
