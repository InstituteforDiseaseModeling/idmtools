<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Singularity Definition Files](#singularity-definition-files)
  - [Available Definition Files](#available-definition-files)
    - [Python Environments](#python-environments)
    - [Other Languages](#other-languages)
    - [Utilities](#utilities)
  - [Quick Start](#quick-start)
    - [Option 1: Build on COMPS (Recommended)](#option-1-build-on-comps-recommended)
    - [Option 2: Build Locally](#option-2-build-locally)
  - [Using Built Images with idmtools](#using-built-images-with-idmtools)
    - [With Python Tasks](#with-python-tasks)
    - [With Generic Tasks (R, Julia, Shell)](#with-generic-tasks-r-julia-shell)
  - [Choosing the Right Definition File](#choosing-the-right-definition-file)
    - [For Quick Prototyping](#for-quick-prototyping)
    - [For General Scientific Computing](#for-general-scientific-computing)
    - [For Machine Learning](#for-machine-learning)
    - [For Disease Modeling](#for-disease-modeling)
    - [For Statistical Analysis](#for-statistical-analysis)
    - [For Multi-Language Projects](#for-multi-language-projects)
  - [Build Times and Sizes](#build-times-and-sizes)
  - [Customizing Definition Files](#customizing-definition-files)
  - [Troubleshooting](#troubleshooting)
    - [Build Fails with "Out of Memory"](#build-fails-with-out-of-memory)
    - ["Module not found" at Runtime](#module-not-found-at-runtime)
    - [Slow Build Times](#slow-build-times)
    - [Image Too Large](#image-too-large)
  - [Best Practices](#best-practices)
  - [Examples](#examples)
  - [Support](#support)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Singularity Definition Files

This directory contains Singularity definition files (.def) for various computational environments. These can be built on COMPS or locally and used with idmtools.

## Available Definition Files

### Python Environments

| File | Description | Build Time | Use Case |
|------|-------------|------------|----------|
| **python_minimal.def** | Minimal Python + NumPy + Matplotlib | ~2-3 min | Quick testing, simple scripts |
| **python_scientific.def** | Full scientific stack (NumPy, SciPy, Pandas, Matplotlib, etc.) | ~10-15 min | Scientific computing, data analysis |
| **python_ml.def** | Machine learning (TensorFlow, PyTorch, Scikit-learn, XGBoost) | ~15-20 min | ML training and inference |
| **epi_modeling.def** | Epidemiological modeling (NetworkX, Mesa, SciPy) | ~10-12 min | Disease modeling, SIR/SEIR models |
| **bioinformatics.def** | Bioinformatics (Biopython, Pysam, Scikit-bio) | ~12-15 min | Genomics, sequence analysis |

### Other Languages

| File | Description | Build Time | Use Case |
|------|-------------|------------|----------|
| **r_analysis.def** | R with tidyverse, data.table, ggplot2 | ~15-20 min | Statistical analysis in R |
| **julia_analysis.def** | Julia with DataFrames, Plots, DifferentialEquations | ~20-25 min | Scientific computing in Julia |
| **multi_language.def** | Python + R + Julia | ~25-30 min | Multi-language workflows |

### Utilities

| File | Description | Build Time | Use Case |
|------|-------------|------------|----------|
| **shell_tools.def** | Shell tools (jq, yq, awk, sed, parallel) | ~3-5 min | Shell scripting, data processing |

## Quick Start

### Option 1: Build on COMPS (Recommended)

```python
from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.utils.singularity_build import SingularityBuildWorkItem

platform = Platform("SlurmStage")

# Build Python scientific environment
sbi = SingularityBuildWorkItem(
    name="Python Scientific Environment",
    definition_file="python_scientific.def",
    image_name="python_scientific.sif"
)

sbi.run(wait_until_done=True, platform=platform)

# Save asset collection ID for reuse
if sbi.succeeded:
    sbi.asset_collection.to_id_file("python_scientific.sif.id")
```

### Option 2: Build Locally

```bash
# Requires root/sudo access
sudo singularity build python_scientific.sif python_scientific.def
```

## Using Built Images with idmtools

### With Python Tasks

```python
from idmtools.assets import AssetCollection
from idmtools.entities import CommandLine
from idmtools_models.python.singularity_json_python_task import SingularityJSONConfiguredPythonTask

# Load the built image
sif_assets = AssetCollection.from_id_file("python_scientific.sif.id")

# Create task
task = SingularityJSONConfiguredPythonTask(script_path="model.py")
task.provided_command = CommandLine(
    "singularity exec ./Assets/python_scientific.sif python3 Assets/model.py"
)
task.common_assets.add_assets(sif_assets)
task.parameters = {"beta": 0.5, "gamma": 0.1}
```

### With Generic Tasks (R, Julia, Shell)

```python
from idmtools_models.singularity_json_task import SingularityJSONConfiguredTask

# R example
r_task = SingularityJSONConfiguredTask()
r_task.provided_command = CommandLine(
    "singularity exec ./Assets/r_analysis.sif Rscript Assets/script.R --config config.json"
)
r_task.common_assets.add_assets(AssetCollection.from_id_file("r_analysis.sif.id"))
r_task.parameters = {"alpha": 0.05, "n_samples": 1000}

# Julia example
julia_task = SingularityJSONConfiguredTask()
julia_task.provided_command = CommandLine(
    "singularity exec ./Assets/julia_analysis.sif julia Assets/simulation.jl"
)
julia_task.common_assets.add_assets(AssetCollection.from_id_file("julia_analysis.sif.id"))
```

## Choosing the Right Definition File

### For Quick Prototyping
→ Use **python_minimal.def** (fastest build)

### For General Scientific Computing
→ Use **python_scientific.def** (comprehensive, well-tested)

### For Machine Learning
→ Use **python_ml.def** (includes TensorFlow, PyTorch)

### For Disease Modeling
→ Use **epi_modeling.def** (optimized for epidemiological models)

### For Statistical Analysis
→ Use **r_analysis.def** (R with tidyverse)

### For Multi-Language Projects
→ Use **multi_language.def** (Python + R + Julia)

## Build Times and Sizes

| Environment | Build Time | Image Size | CPU Cores Used |
|-------------|------------|------------|----------------|
| python_minimal | 2-3 min | ~500 MB | 1-2 |
| python_scientific | 10-15 min | ~2 GB | 2-4 |
| python_ml | 15-20 min | ~3 GB | 4-8 |
| r_analysis | 15-20 min | ~2.5 GB | 2-4 |
| julia_analysis | 20-25 min | ~2 GB | 2-4 |
| multi_language | 25-30 min | ~4 GB | 4-8 |

*Note: Build times on COMPS may vary based on cluster load*

## Customizing Definition Files

To add packages to an existing definition:

```singularity
%post
    # ... existing packages ...

    # Add your custom packages
    pip3 install --no-cache-dir \
        your_package_1 \
        your_package_2
```

Then rebuild:
```python
sbi = SingularityBuildWorkItem(
    name="Custom Environment",
    definition_file="custom.def",
    image_name="custom.sif"
)
```

## Troubleshooting

### Build Fails with "Out of Memory"
→ Use a smaller definition file or reduce concurrent package installations

### "Module not found" at Runtime
→ Verify the package is listed in the %post section
→ Check package versions are compatible

### Slow Build Times
→ Use **python_minimal.def** for testing
→ Build during off-peak hours on COMPS
→ Consider caching intermediate layers (advanced)

### Image Too Large
→ Remove unused packages from %post
→ Use `--no-cache-dir` with pip
→ Clean up apt cache in %post

## Best Practices

1. **Start Small**: Begin with minimal definitions and add packages as needed
2. **Version Pin**: Specify package versions for reproducibility (e.g., `numpy>=1.24.0`)
3. **Reuse Images**: Save `.sif.id` files and reuse across experiments
4. **Clean Build Environment**: Always include cleanup commands in %post
5. **Test Locally First**: If possible, test builds locally before COMPS
6. **Document Dependencies**: Add comments explaining why each package is needed

## Examples

See `../generic_singularity_task_example.py` for complete working examples of using these definition files.

See `../../tutorials/parameter_sweeps/` for epidemiological modeling examples.

## Support

For issues or questions:
- Check the idmtools documentation
- Review existing examples in `examples/singularity/`
- Open an issue on the idmtools GitHub repository
