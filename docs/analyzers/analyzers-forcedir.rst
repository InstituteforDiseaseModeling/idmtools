=======================
Force working directory
=======================

You can force analyzers to use a specific working directory other than the default, which is the directory from which the analyzer is run. For example, if you install |IT_s| to the **\\idmtools** directory and then run one of the example analyzers from their default directory, **\\examples\\analyzers**, then the default working directory would be **\\idmtools\\examples\\analyzers**.

To force a working directory, you use the :py:attr:`force_manager_working_directory` parameter from the :py:class:`~idmtools.analysis.analyze_manager.AnalyzeManager` class. The following python code, using the :py:class:`~idmtools.analysis.download_analyzer.DownloadAnalyzer` as an example , illustrates different ways on how to use and configure the :py:attr:`force_manager_working_directory` parameter and how it works and interacts with the :py:attr:`working_dir` parameter::


    from idmtools.analysis.analyze_manager import AnalyzeManager
    from idmtools.analysis.download_analyzer import DownloadAnalyzer
    from idmtools.core import ItemType
    from idmtools.core.platform_factory import Platform

    if __name__ == '__main__':
        platform = Platform('COMPS2')
        filenames = ['StdOut.txt']
        experiment_id = '11052582-83da-e911-a2be-f0921c167861'  # comps2 staging exp id

    # force_manager_working_directory = False (default value):
    # Analyzers will use their own specified working_dir if available. If not, the AnalyzeManager
    # specified working_dir will be used (default: '.').
    #
    # force_manager_working_directory = True
    # Analyzers will use the AnalyzeManager specified working_dir (default: '.')

    # Examples

    # This will use the default working_dir for both analyzers (the current run directory, '.')
    analyzers = [DownloadAnalyzer(filenames=filenames, output_path='DL1'),
                 DownloadAnalyzer(filenames=filenames, output_path='DL2')]
    manager = AnalyzeManager(platform=platform, ids=[(experiment_id, ItemType.EXPERIMENT)],
                             analyzers=analyzers)
    manager.analyze()

    # This will use the manager-specified working_dir for both analyzers
    analyzers = [DownloadAnalyzer(filenames=filenames, output_path='DL1'),
                 DownloadAnalyzer(filenames=filenames, output_path='DL2')]
    manager = AnalyzeManager(platform=platform, ids=[(experiment_id, ItemType.EXPERIMENT)],
                             analyzers=analyzers, working_dir='use_this_working_dir_for_both_analyzers')
    manager.analyze()

    # This will use the analyzer-specified working_dir for DL1 and the manager-specified dir for DL2
    analyzers = [DownloadAnalyzer(filenames=filenames, output_path='Dl1', working_dir='DL1_working_dir'),
                 DownloadAnalyzer(filenames=filenames, output_path='DL2')]
    manager = AnalyzeManager(platform=platform, ids=[(experiment_id, ItemType.EXPERIMENT)],
                             analyzers=analyzers, working_dir='use_this_working_dir_if_not_set_by_analyzer')
    manager.analyze()

    # This will use the manager-specified dir for both DL1 and DL2, even though DL1 tried to set its own
    analyzers = [DownloadAnalyzer(filenames=filenames, output_path='DL1', working_dir='DL1_working_dir'),
                 DownloadAnalyzer(filenames=filenames, output_path='DL2')]
    manager = AnalyzeManager(platform=platform, ids=[(experiment_id, ItemType.EXPERIMENT)],
                             analyzers=analyzers, working_dir='use_this_working_dir_if_not_set_by_analyzer',
                             force_manager_working_directory=True)
    manager.analyze()