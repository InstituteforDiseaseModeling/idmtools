"""
In this example, we will demonstrate how to use WorkOrder.json to override simulation command with comp's scheduling
feature. also show how to use WorkOrder's Environment field to set PYTHONPATH for model.
       in COMPS, file layout is:
        Assets-
              |_MyExternalLibarary
                       |_function.py
              |_model1.py
              |_site-packages
                    |_numpy
        in order for model1.py to call MyExternalLibarary.function which uses numpy package, MyExternalLibarary.function
        and numpy must be in PYTHONPATH
        So we add "PYTHONPATH": "$PYTHONPATH:$PWD/Assets:$PWD/Assets/site-packages" in WorkOrder.json
        the command also define in WorkOrder.json as: "Command": "python3 Assets/model1.py". you can define other fields
        in WorkOrder, like NumCores, NumProcesses etc.
"""


import os
import sys

from idmtools.assets import AssetCollection
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_platform_comps.utils.schedule_simulations import add_work_order
from idmtools_platform_comps.utils.python_requirements_ac.requirements_to_asset_collection import \
    RequirementsToAssetCollection

with Platform('CALCULON') as platform:
    # install numpy package to cluster
    pl = RequirementsToAssetCollection(platform, pkg_list=['numpy==1.19.5'])
    ac_id = pl.run()
    # add numpy to common_assets
    common_assets1 = AssetCollection.from_id(ac_id, as_copy=True)
    # add input folder to common_assets
    common_assets2 = AssetCollection.from_directory(os.path.join("inputs", "python", "MyExternalLibrary"), relative_path="MyExternalLibrary")
    # add both together
    common_assets = common_assets1 + common_assets2

    # create json config task which generates config.json and add model script and common assets to comps experiment
    task = JSONConfiguredPythonTask(
        script_path=os.path.join("inputs", "python", "Assets", "model1.py"),
        # set default parameters
        parameters=dict(c=0),
        # set a parameter envelope
        envelope="parameters",
        # add some experiment level assets
        common_assets=common_assets
    )

    # create templatedsimulation
    ts = TemplatedSimulations(base_task=task)

    # add WorkOrder.json to each simulation as transient_assets
    add_work_order(ts, file_path=os.path.join("inputs", "scheduling", "WorkOrder.json"))

    # create build and define our sweeps
    builder = SimulationBuilder()
    builder.add_sweep_definition(JSONConfiguredPythonTask.set_parameter_partial("a"), range(3))
    builder.add_sweep_definition(JSONConfiguredPythonTask.set_parameter_partial("b"), [1, 2])
    # add builder to templatedsimulation
    ts.add_builder(builder)
    # create experiment
    e = Experiment.from_template(ts, name=os.path.split(sys.argv[0])[1], tags=dict(tag1=1))
    # run experiment with scheduling
    e.run(wait_until_done=True, scheduling=True)
    # use system status as the exit code
    sys.exit(0 if e.succeeded else -1)
