from examples.ssmt.simple_analysis.analyzers.AdultVectorsAnalyzer import AdultVectorsAnalyzer
from examples.ssmt.simple_analysis.analyzers.PopulationAnalyzer import PopulationAnalyzer
from idmtools.core.platform_factory import Platform
from idmtools.analysis.platform_anaylsis import PlatformAnalysis

if __name__ == "__main__":
    platform = Platform('BELEGOST')
    analysis = PlatformAnalysis(
        platform=platform, experiment_ids=["b716f387-cb04-eb11-a2c7-c4346bcb1553"],
        analyzers=[PopulationAnalyzer, AdultVectorsAnalyzer], analyzers_args=[{'title': 'idm'}, {'name': 'global good'}],
        analysis_name="SSMT Analysis Simple 1",
        # You can pass any additional arguments needed to AnalyzerManager through the extra_args parameter
        extra_args=dict(max_workers=8)
    )

    analysis.analyze(check_status=True)
    wi = analysis.get_work_item()
    print(wi)
