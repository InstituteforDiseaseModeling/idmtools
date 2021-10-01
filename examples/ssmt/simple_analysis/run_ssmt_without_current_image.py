# this example allow user to test ssmt image without needing a new docker image
# it uploads local core and comps packages and installs them remotely before running anything.
# script to use test ssmt changes without build and deploy ssmt docker image to artifactory
# steps:
# cd idmtools && pymake dist
# cd idmtools_platform_comps && pymake dist
# run this example (may need to change to specific platform)

from pathlib import PurePath
from idmtools import __version__ as core_version
from idmtools.analysis.platform_anaylsis import PlatformAnalysis
from idmtools.core.platform_factory import Platform
from idmtools_platform_comps import __version__ as platform_comps_version
import tempfile
from idmtools.assets import AssetCollection
from examples.ssmt.simple_analysis.analyzers.PopulationAnalyzer import PopulationAnalyzer
CORE_VERSION = core_version.replace('nightly.0', 'nightly')
COMPS_VERSION = platform_comps_version.replace('nightly.0', 'nightly')
COMPS_PACKAGE_FILENAME = f"idmtools_platform_comps-{COMPS_VERSION}.tar.gz"
CORE_PACKAGE_FILENAME = f"idmtools-{CORE_VERSION}.tar.gz"
CURRENT_DIR = PurePath(__file__).parent
COMPS_LOCAL_PACKAGE = CURRENT_DIR.parent.parent.parent.joinpath("idmtools_platform_comps", "dist", COMPS_PACKAGE_FILENAME)
CORE_LOCAL_PACKAGE = CURRENT_DIR.parent.parent.parent.joinpath("idmtools_core", "dist", CORE_PACKAGE_FILENAME)
COMPS_LOAD_SSMT_PACKAGES_WRAPPER = f"""
set -o noglob
echo Running $@ 

echo after install of newer idmtools

export PYTHONPATH=$(pwd)/Assets/site-packages:$(pwd)/Assets/:$PYTHONPATH

echo "Installing updated versions of idmtools packages"
pip install Assets/{COMPS_PACKAGE_FILENAME} --force-reinstall --no-cache-dir --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
pip install Assets/{CORE_PACKAGE_FILENAME} --force-reinstall --no-cache-dir --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple

$@
"""


def write_wrapper_script():
    f = tempfile.NamedTemporaryFile(suffix='.sh', mode='wb', delete=False)
    f.write(COMPS_LOAD_SSMT_PACKAGES_WRAPPER.replace("\r", "").encode('utf-8'))
    f.flush()
    return f.name


wrapper = write_wrapper_script()


def pre_load_func():
    print("!!!!!!!!!!!!!Preload executed!!!!!!!!!!!!!!!!!!")
    from idmtools import __version__ as core_version
    from idmtools_platform_comps import __version__ as comps_version
    print(f"Idmtools Core Version: {core_version}")
    print(f"Idmtools COMPS Version: {comps_version}")


platform = Platform('Slurm2')
analysis = PlatformAnalysis(platform=platform, experiment_ids=["c348452d-921c-ec11-92e0-f0921c167864"],
                            analyzers=[PopulationAnalyzer],
                            analyzers_args=[{'title': 'idm'}], analysis_name="SSMT Analysis Simple no image",
                            extra_args=dict(max_workers=8),
                            asset_files=AssetCollection([CORE_LOCAL_PACKAGE, COMPS_LOCAL_PACKAGE]),
                            pre_run_func=pre_load_func,
                            wrapper_shell_script=wrapper)

analysis.analyze(check_status=True)
wi = analysis.get_work_item()
