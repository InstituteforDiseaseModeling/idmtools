import copy
from functools import partial
from logging import getLogger
import numpy
from idmtools.assets import AssetCollection
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities import CommandLine
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform import IPlatform
from idmtools.entities.simulation import Simulation
from idmtools_models.templated_script_task import LINUX_PYTHON_PATH_WRAPPER, get_script_wrapper_unix_task
from idmtools_platform_comps.utils.python_requirements_ac.requirements_to_asset_collection import RequirementsToAssetCollection

command_format_str = "python3 Assets/sir.py --N {n} --I0 {i0} --R0 {r0} --gamma {gamma} --beta {beta}"
user_logger = getLogger('user')


def create_config_before_provisioning(simulation: Simulation, platform: IPlatform):
    # set the command dynamically
    simulation.task.command = CommandLine.from_string(command_format_str.format(**simulation.task.config))
    user_logger.info(f"Set command for simulation to: {simulation.task.command}")
    # return configs as tags
    return copy.deepcopy(simulation.task.config)


def set_value(simulation, name, value):
    simulation.task.config[name] = round(value, 2) if isinstance(value, float) else value
    # add tag with our value
    simulation.tags[name] = round(value, 2) if isinstance(value, float) else value
    #user_logger.info(f"Set config for {name} to {value}")


platform = Platform("CALCULON")
pl = RequirementsToAssetCollection(platform, pkg_list=['numpy', 'matplotlib', 'scipy'])
ac_id = pl.run()
ac = AssetCollection.from_id(ac_id, as_copy=True)
ac.add_asset("sir.py")
base_task = CommandTask(command="python3 Assets/sir.py", common_assets=ac)
wrapper_task = get_script_wrapper_unix_task(base_task, template_content=LINUX_PYTHON_PATH_WRAPPER)
base_task.config = dict(n=1000, i0=1, r0=0, beta=0.2, gamma=1./10)
base_task.add_pre_creation_hook(create_config_before_provisioning)

sb = SimulationBuilder()
# Add sweeps on 3 parameters. Total of 1680 simulations(6x14x21)
sb.add_sweep_definition(partial(set_value, name="i0"), range(20, 260, 40)) # 6
sb.add_sweep_definition(partial(set_value, name="gamma"), numpy.arange(0.1, 0.8, 0.05)) # 14
sb.add_sweep_definition(partial(set_value, name="beta"), numpy.arange(0.01, 1, 0.05)) # 21

experiment = Experiment.from_builder(sb, base_task=wrapper_task, name="Demo Hooks")
experiment.run(wait_until_done=True)
