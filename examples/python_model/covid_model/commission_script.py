
from covid_ssmt import COVID19SSMT
from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.analysis.download_analyzer import DownloadAnalyzer
from idmtools.core.platform_factory import Platform


if __name__ == "__main__":
    # Create a platform to run the workitem
    platform = Platform('COMPS2')

    # Create a COVIDSSMT worker
    wi = COVID19SSMT(item_name="COVID run",
                     covid_abm_path="covid_abm",
                     run_script="user_script.py")

    # Add a custom library: covid_seattle to our assets
    wi.asset_files.add_path("covid_seattle", relative_path="pyPackages/covid_seattle", recursive=True)

    # Wait for it to complete
    wi.run(wait_on_done=True, platform=platform)

    # Download its outputs
    analyzer = DownloadAnalyzer(["seattle_projections_v3.png", "seattle-projection-results_v4e.obj"])
    am = AnalyzeManager(platform=platform, analyzers=[analyzer])
    am.add_item(wi)
    am.analyze()
