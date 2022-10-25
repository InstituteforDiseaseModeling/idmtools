from examples.ssmt.partial_analyzer.MyCSVAnalayzer import MyCSVAnalyzer
from idmtools.core.platform_factory import Platform
from idmtools.analysis.platform_anaylsis import PlatformAnalysis

if __name__ == "__main__":
    platform = Platform('Calculon')
    analysis = PlatformAnalysis(
        platform=platform, experiment_ids=["76c4f919-f0d2-ec11-a9f8-b88303911bc1"],
        analyzers=[MyCSVAnalyzer], analyzers_args=[{'filenames': ['output/a.csv'], 'output_path': 'output'}],
        analysis_name="SSMT partial analyzer",
        # Only analyzer succeed sims
        extra_args=dict(partial_analyze_ok=True)
    )

    analysis.analyze(check_status=True)
    wi = analysis.get_work_item()
    print(wi)
