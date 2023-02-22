
import tempfile
from pathlib import Path
from typing import List
from jinja2 import Environment, FileSystemLoader
from examples.ssmt.ssmt_with_custom_packages.NewInfectionsAnalyzer import NewInfectionsAnalyzer
from idmtools.core.platform_factory import Platform
from idmtools.analysis.platform_anaylsis import PlatformAnalysis


def write_wrapper_script(list_of_packages: List[str]):
    env = Environment(loader=FileSystemLoader(Path(__file__).parent))
    template = env.get_template('package_script.sh.jinja2')
    f = tempfile.NamedTemporaryFile(suffix='.sh', mode='wb', delete=False)
    f.write(template.render(dict(packages=list_of_packages)).replace("\r", "").encode('utf-8'))
    f.flush()
    return f.name


if __name__ == "__main__":
    platform = Platform('Calculon')
    analysis = PlatformAnalysis(
        platform=platform, experiment_ids=["d66a72ee-74a9-ed11-aa02-b88303911bc1"],
        analyzers=[NewInfectionsAnalyzer], #analyzers_args=[{'name': 'plot new infections'}],
        analysis_name="Example to use extra packages",
        wrapper_shell_script=write_wrapper_script(['kaleido', 'plotly']),
        # You can pass any additional arguments needed to AnalyzerManager through the extra_args parameter
        extra_args=dict(max_workers=8)
    )

    analysis.analyze(check_status=True)
    wi = analysis.get_work_item()
    print(wi)