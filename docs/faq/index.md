# Frequently asked questions

Common questions about idmtools.

## Installation

### Q: Which Python versions are supported?

A: Python 3.10+ (64-bit only).

### Q: Do I need to install all platforms?

A: No! Use `pip install idmtools[platform]` to install only what you need. See [Installation Guide](../getting-started/installation.md).

### Q: Do I need login to Docker Hub or GitHub Container Registry?

A: No, all docker images are public unless you want to push your docker image to Github Container Registry which is
idmtools default docker registry.

## Usage

### Q: How do I choose between platforms?

A: See [Platform Comparison](../platforms/index.md#platform-comparison) for guidance.

### Q: Can I run simulations locally without a cluster?

A: Yes! Use the Container platform. See [Platform Overview](../platforms/index.md).

### Q: How do I debug failed simulations?

A: Check simulation logs, stderr.txt file, use docker container platform for local testing, and enable verbose logging.

## Performance

### Q: How many simulations can I run at once?

A: Depends on platform:

- COMPS: Thousands or more
- Slurm: Cluster-dependent
- Container: Limited by local resources

### Q: How do I speed up parameter sweeps?

A: Use batch execution, optimize simulation code, and choose the right platform. See [Parameter Sweeps](../tutorials/parameter-sweeps.md).

## Errors

### Q: "Module not found" error

A: Ensure idmtools is installed: `pip install idmtools[full]`. Or pip install complained model

### Q: Platform connection failed

A: Check your configuration and network connectivity. See [Configuration](../getting-started/configuration.md).

### Q: Out of memory errors

A: Reduce batch size, use fewer workers, or increase system resources.

## Common workflow questions

### Q: How do I check if my experiment is still running?

Use `experiment.status` after calling `experiment.run()`, or check the platform's web interface (e.g., COMPS portal).
Or use idmtools cli command for Container and Slurm platforms.

### Q: Why is my `config.json` empty?

Make sure you pass a JSON string to `Asset(content=..., filename=config.json)`, not a Python dict. Use `json.dumps(config)` to convert.

### Q: How do I add files my model needs?

Use `experiment.assets` for files shared across all simulations, and `simulation.assets` for per-simulation files.

### Q: Can I run experiments locally for testing?

Yes, use `Platform("Container")` to run experiments locally using Docker containers.

### Q: How do I rerun a failed experiment?

You can retrieve an existing experiment by ID and resubmit:

```python
from idmtools.core.platform_factory import Platform

platform = Platform("COMPS")
experiment = platform.get_item(item_id="<experiment_id>", item_type="experiment")
experiment.run(wait_until_done=True, platform)
```

### Q: How do I pass parameters to my model?

Use `JSONConfiguredPythonTask` which automatically writes a `config.json` file that your model reads. Alternatively,
use `CommandLine` to pass arguments directly. See [Parameter Sweeps](../tutorials/parameter-sweeps.md).

## Getting help

Can't find your answer?

- Check the [User guide](../user-guide/index.md)
- Browse [Tutorials](../tutorials/index.md)
- Search the [API eeference](../api/index.md)
- Open an issue on [GitHub](https://github.com/institutefordiseasemodeling/idmtools/issues)
