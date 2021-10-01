from idmtools.analysis.download_analyzer import DownloadAnalyzer
from idmtools.core.platform_factory import Platform
from idmtools.analysis.platform_anaylsis import PlatformAnalysis

docker_image = "docker-staging.packages.idmod.org/idmtools/comps_ssmt_worker:1.6.3.23"

if __name__ == "__main__":
    platform = Platform('BAYESIAN', docker_image=docker_image)
    analysis = PlatformAnalysis(
        platform=platform, work_item_ids=["aa3189a6-d51e-ec11-92e0-f0921c167864"],
        analyzers=[DownloadAnalyzer], analyzers_args=[{'filenames': ['StdOut.txt'], 'output_path': 'output'}],
        analysis_name="SSMT Analysis Wi Simple 1",
        # You can pass any additional arguments needed to AnalyzerManager through the extra_args parameter
        extra_args=dict(max_workers=8)
    )

    analysis.analyze(check_status=True)
    wi = analysis.get_work_item()
    print(wi)
