# API Reference

Complete API documentation for idmtools.

## Core Modules

### [idmtools.core](core.md)
Core classes and functionality

**Key Classes:**

- `Platform` - Platform factory and management
- `Entity` - Base entity class
- `ItemType` - Entity type enumeration

### [idmtools.models](models.md)
Model implementations

**Modules:**

- `python` - Python model support
  - PythonTask
  - JSONConfiguredTask
  - SingularityJSONConfiguredTask
- `r` - R model support
- `templated_script_task` - Templated models



### [idmtools.platforms](platforms.md)
Platform implementations

**Platform Types:**

- `comps` - COMPS platform
- `slurm` - Slurm platform
- `container` - Container platform
- `process` - Local process platforms

## API Navigation

Browse by module or use the search function to find specific classes and functions.

## See Also

- [User Guide](../user-guide/index.md) - How to use the API
- [Tutorials](../tutorials/index.md) - API usage examples
- [CLI Reference](../cli/index.md) - Command-line tools
