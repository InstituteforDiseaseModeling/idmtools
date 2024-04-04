from idmtools.analysis.download_analyzer import DownloadAnalyzer
from idmtools.core.platform_factory import Platform
from idmtools.analysis.platform_anaylsis import PlatformAnalysis

#docker_image = "docker-staging.packages.idmod.org/idmtools/comps_ssmt_worker:1.6.3.23"

if __name__ == "__main__":
    platform = Platform('CALCULON') #, docker_image=docker_image)
    analysis = PlatformAnalysis(
        platform=platform, work_item_ids=["3c5cc8c2-21f1-ee11-aa12-b88303911bc1"],
        analyzers=[DownloadAnalyzer], analyzers_args=[{'filenames': ['stdout.txt'], 'output_path': 'output'}],
        analysis_name="SSMT Analysis Wi Simple 1",
        # You can pass any additional arguments needed to AnalyzerManager through the extra_args parameter
        extra_args=dict(max_workers=8)
    )

    analysis.analyze(check_status=True)
    wi = analysis.get_work_item()
    print(wi)
