# Asset management

Assets are files your simulations need to run — scripts, data files, config files, container images, etc. They are managed through `AssetCollection` and attached to tasks or experiments.

## Adding assets to a task

Use `task.common_assets` to add files shared across all simulations that use this task:

```python
from idmtools.assets import AssetCollection

# Add a single file
task.common_assets.add_asset("model.py")

# Add from an existing AssetCollection by its platform ID
task.common_assets.add_assets(AssetCollection.from_id("c94763e4-8f55-ed11-a9ff-b88303911bc1"))
```

## Adding assets to an experiment

Assets added at the experiment level are shared across all simulations — useful for large files you don't want to duplicate per simulation:

```python
import os
from idmtools.assets import AssetCollection

# Add a single file directly to the experiment
experiment.add_asset(os.path.join("inputs", "test_interventions.py"))

# Load a shared asset collection (as_copy=True makes it mutable)
common_assets = AssetCollection.from_id('707985f2-0e09-f111-9318-f0921c167864', as_copy=True)
experiment.add_assets(common_assets)
```

## common_assets vs transient_assets

| | `common_assets` | `transient_assets` |
|---|---|---|
| Scope | Shared across all simulations | Per-simulation only |
| Use for | Model scripts, container images, shared data | Per-sim config files |
| Uploaded | Once per experiment | Once per simulation |

```python
# Shared across all simulations (e.g. model script, .sif image)
task.common_assets.add_asset("model.py")

# Per-simulation files (e.g. individual config)
task.transient_assets.add_asset("config.json")
```

## AssetCollection from ID file

When working with Singularity images on COMPS/Slurm, use an `.id` file to reference a previously uploaded asset:

```python
from idmtools.assets import AssetCollection

# Load .sif image from its asset ID file
task.common_assets.add_assets(AssetCollection.from_id_file("python_minimal.sif.id"))
```

## Next steps

- [Creating Simulations & Experiments](creating-simulations.md) - Use assets in simulations
- [Parameter Sweeps](../tutorials/parameter-sweeps.md) - Assets in parameter sweeps
- [Singularity Tutorial](../tutorials/singularity.md) - Managing container image assets
