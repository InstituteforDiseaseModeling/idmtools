from examples.ssmt.simple_analysis.analyzers.AdultVectorsAnalyzer import AdultVectorsAnalyzer
from examples.ssmt.simple_analysis.analyzers.PopulationAnalyzer import PopulationAnalyzer
from idmtools.ssmt.ssmt_analysis import SSMTAnalysis

if __name__ == "__main__":

    analysis = SSMTAnalysis(experiment_ids=["8bb8ae8f-793c-ea11-a2be-f0921c167861"],
                            analyzers=[PopulationAnalyzer, AdultVectorsAnalyzer],
                            analyzers_args=[{'title': 'idm'}, {'name': 'global good'}],
                            analysis_name="SSMT Analysis Simple 1")

    analysis.analyze(check_status=True)
