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
    - `PythonTask`
    - `JSONConfiguredPythonTask`
    - `SingularityJSONConfiguredPythonTask`
- `r` - R model support
- `templated_script_task` - Templated models



### [idmtools.platforms](platforms.md)
Platform implementations

**Platform Types:**

- `comps` - COMPS platform
- `slurm` - Slurm platform
- `container` - Container platform
- `process` - Local process platforms

### [Data Analysis](../data-analysis/index.md)
Analysis framework for post-processing simulation outputs

**Key Classes:**

- `IAnalyzer` - Abstract base class for all analyzers
- `AnalyzeManager` - Run analyzers locally with a parallel worker pool
- `PlatformAnalysis` - Run analyzers remotely on COMPS via SSMT
- `DownloadAnalyzer`, `CSVAnalyzer`, `TagsAnalyzer`, `AddAnalyzer` - Built-in analyzers

## API Navigation

Browse by module or use the search function to find specific classes and functions.

## See Also

- [User Guide](../user-guide/index.md) - How to use the API
- [Tutorials](../tutorials/index.md) - API usage examples
- [CLI Reference](../cli/index.md) - Command-line tools
