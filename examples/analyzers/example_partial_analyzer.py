from idmtools.analysis.download_analyzer import DownloadAnalyzer
from idmtools.core.platform_factory import Platform
from idmtools.analysis.platform_anaylsis import PlatformAnalysis

if __name__ == "__main__":
    platform = Platform('CALCULON')
    analysis = PlatformAnalysis(
        platform=platform, experiment_ids=["c2d8602d-457d-ec11-a9f3-9440c9be2c51"],
        analyzers=[DownloadAnalyzer], analyzers_args=[{'filenames': ["stderr.txt"], 'output_path': 'output'}],
        analysis_name="SSMT Analysis Simple partial",
        # You can pass any additional arguments needed to AnalyzerManager through the extra_args parameter
        extra_args=dict(partial_analyze_ok=True)
    )

    analysis.analyze(check_status=True)
    wi = analysis.get_work_item()
    print(wi)