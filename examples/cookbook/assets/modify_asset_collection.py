# This recipes demos how to extend/modify and existing AssetCollection
from idmtools.assets import AssetCollection, Asset
from idmtools.core.platform_factory import Platform

with Platform("CALCULON") as platform:
    # first we start by loading our existing asset collection
    existing_ac = AssetCollection.from_id("50002755-20f1-ee11-aa12-b88303911bc1")  # comps asset id
    # now we want to add one file to it. Since asset collection on the server our immutable, what we can do is the following
    #
    # create a new asset collection object
    ac = AssetCollection(existing_ac)
    # or
    # ac = AssetCollection.from_id("98d329b5-95d6-ea11-a2c0-f0921c167862", as_copy=True)
    # ac = existing_ac.copy()
    # ac = AssetCollection()
    # ac += existing_ac
    # add our items to the new collection
    ac.add_asset(Asset(filename="Example", content="Blah"))

    # then depending on the workflow, we can create directly or use within an Experiment/Task/Simulation
    platform.create_items(ac)

    # Experiment
    # e = Experiment.from_task(..., assets=ac)

    # Task
    # task = CommandTask(common_assets = ac)
    # or
    # task.common_assets = ac
