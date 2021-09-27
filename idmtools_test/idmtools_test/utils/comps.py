import functools
import os
import subprocess
import sys
import tempfile
from pathlib import PurePath
from COMPS import Data
from COMPS.Data import AssetCollection as CompsAssetCollection
from COMPS.Data import QueryCriteria, Simulation as COMPSSimulation, Experiment as COMPSExperiment
from idmtools import __version__ as core_version
from idmtools.builders import SimulationBuilder
from idmtools.core.enums import EntityStatus
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform import IPlatform
from idmtools_models.templated_script_task import get_script_wrapper_unix_task
from idmtools_platform_comps import __version__ as platform_comps_version

CURRENT_DIR = PurePath(__file__).parent
COMPS_VERSION = platform_comps_version.replace('nightly.0', 'nightly')
if COMPS_VERSION.endswith(".0") and len(COMPS_VERSION) == 7:
    COMPS_VERSION = ".".join(COMPS_VERSION.split(".")[:3])
CORE_VERSION = core_version.replace('nightly.0', 'nightly')
if CORE_VERSION.endswith(".0") and len(CORE_VERSION) == 7:
    CORE_VERSION = ".".join(CORE_VERSION.split(".")[:3])
COMPS_PACKAGE_FILENAME = f"idmtools_platform_comps-{COMPS_VERSION}.tar.gz"
CORE_PACKAGE_FILENAME = f"idmtools-{CORE_VERSION}.tar.gz"
COMPS_LOCAL_PACKAGE = CURRENT_DIR.parent.parent.parent.joinpath("idmtools_platform_comps", "dist", COMPS_PACKAGE_FILENAME)
CORE_LOCAL_PACKAGE = CURRENT_DIR.parent.parent.parent.joinpath("idmtools_core", "dist", CORE_PACKAGE_FILENAME)
COMPS_LOAD_SSMT_PACKAGES_WRAPPER = f"""
set -o noglob
echo Running $@ 

echo after install of newer idmtools

export PYTHONPATH=$(pwd)/Assets/site-packages:$(pwd)/Assets/:$PYTHONPATH

echo "Installing updated versions of idmtools packages"
pip install Assets/{COMPS_PACKAGE_FILENAME} --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
pip install Assets/{CORE_PACKAGE_FILENAME} --force --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple

$@
"""


@functools.lru_cache(1)
def write_wrapper_script():
    f = tempfile.NamedTemporaryFile(suffix='.sh', mode='wb', delete=False)
    f.write(COMPS_LOAD_SSMT_PACKAGES_WRAPPER.replace("\r", "").encode('utf-8'))
    f.flush()
    return f.name


def load_library_dynamically(item, platform: IPlatform):
    fn = write_wrapper_script()
    for file in [COMPS_LOCAL_PACKAGE, CORE_LOCAL_PACKAGE]:
        item.assets.add_asset(file)
    item.task = get_script_wrapper_unix_task(task=item.task, template_content=COMPS_LOAD_SSMT_PACKAGES_WRAPPER)
    item.task.gather_common_assets()
    item.task.pre_creation(item, platform)
    # item.assets.add_assets(item.task.gather_common_assets(), fail_on_duplicate=False)


def run_package_dists():
    mk = "pymake" if sys.platform == "win32" else "make"
    print("Running Dist for core")
    subprocess.call(f"{mk} dist", cwd=CORE_LOCAL_PACKAGE.parent.parent, shell=True)
    print("Running Dist for comps")
    subprocess.call(f"{mk} dist", cwd=COMPS_LOCAL_PACKAGE.parent.parent, shell=True)


def get_asset_collection_id_for_simulation_id(sim_id):
    """
    Obtains COMPS AssetCollection id from a given simulation id.
    :param sim_id: A simulation id to retrieve assetcollection id from
    :return: COMPS AssetCollection id
    """
    simulation = COMPSSimulation.get(sim_id, query_criteria=QueryCriteria().select(
        ['id', 'experiment_id']).select_children(
        ["files", "configuration"]))

    if simulation.configuration is None:
        # check experiment
        experiment = COMPSExperiment.get(simulation.experiment_id, query_criteria=QueryCriteria().select(
            ['id']).select_children("configuration")
        )
        collection_id = experiment.configuration.asset_collection_id
    else:
        collection_id = simulation.configuration.asset_collection_id
    return collection_id


def get_asset_collection_by_id(collection_id, query_criteria=None) -> CompsAssetCollection:
    """
    Obtains COMPS AssetCollection from a given collection id.
    :param collection_id: An asset collection id to retrieve assetcollection from
    :param query_criteria: query_criteria
    :return: COMPS AssetCollection
    """
    query_criteria = query_criteria or QueryCriteria().select_children('assets')
    try:
        return Data.AssetCollection.get(collection_id, query_criteria)
    except (RuntimeError, ValueError):
        return None


def sims_from_experiment(e):
    o = e
    if isinstance(e, Experiment):
        o = e.get_platform_object()
    return o.get_simulations(QueryCriteria().select(['id', 'state']).select_children('hpc_jobs'))


def workdirs_from_simulations(sims):
    return {str(sim.id): sim.hpc_jobs[-1].working_directory for sim in sims if sim.hpc_jobs}


def get_simulation_path(simulation):
    path = workdirs_from_simulations([simulation])[str(simulation.id)]
    return path


def get_simulation_by_id(sim_id, query_criteria=None):
    return COMPSSimulation.get(id=sim_id, query_criteria=query_criteria)


def assure_running_then_wait_til_done(tst, experiment):
    tst.platform.run_items(items=[experiment])
    tst.platform.refresh_status(item=experiment)
    tst.assertFalse(experiment.done)
    tst.assertTrue(all([s.status == EntityStatus.RUNNING for s in experiment.simulations]))
    # Wait till done
    import time
    start_time = time.time()
    while time.time() - start_time < 180:
        tst.platform.refresh_status(item=experiment)
        if experiment.done:
            break
        time.sleep(3)
    tst.assertTrue(experiment.done)


def setup_test_with_platform_and_simple_sweep(tst):
    from idmtools.core.platform_factory import Platform
    tst.platform = Platform('SLURM2')
    print(tst.case_name)

    def setP(simulation, p):
        return simulation.task.set_parameter("P", p)

    tst.builder = SimulationBuilder()
    tst.builder.add_sweep_definition(setP, [1, 2, 3])

