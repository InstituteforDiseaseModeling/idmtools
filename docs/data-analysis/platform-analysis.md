# PlatformAnalysis

`PlatformAnalysis` runs analyzers as a remote **SSMT** work item on COMPS, rather than locally. Simulation output files stay on the cluster, eliminating the need to transfer large datasets to your local machine.

## What can PlatformAnalysis do?

- Submit analyzer jobs directly to COMPS as SSMT work items
- Keep simulation data on the cluster — no large file downloads
- Run the same [`IAnalyzer`](analyzers.md) classes you use with [`AnalyzeManager`](analyze-manager.md)
- Pass constructor arguments per-analyzer via `analyzers_args`
- Forward extra [`AnalyzeManager`](analyze-manager.md) options (e.g. `partial_analyze_ok`) to the remote run via `extra_args`
- Attach additional files, assets, or a custom idmtools config for the remote environment

!!! note "COMPS only"
    `PlatformAnalysis` requires the `idmtools-platform-comps` package and a COMPS platform. For local analysis on any platform, use [`AnalyzeManager`](analyze-manager.md) instead.

## Import

```python
from idmtools.analysis.platform_anaylsis import PlatformAnalysis
from idmtools.core.platform_factory import Platform
```

## Constructor parameters

```python
PlatformAnalysis(
    platform,
    analyzers,
    experiment_ids=[],
    simulation_ids=[],
    work_item_ids=[],
    analyzers_args=None,
    analysis_name='WorkItem Test',
    tags=None,
    additional_files=None,
    asset_collection_id=None,
    asset_files=None,
    wait_till_done=True,
    idmtools_config=None,
    pre_run_func=None,
    wrapper_shell_script=None,
    verbose=False,
    extra_args=None,
)
```

### Key parameters

#### `analyzers`

**Type:** `List[Type[IAnalyzer]]`  **Required**

A list of **analyzer classes** (not instances). Unlike `AnalyzeManager`, which takes instantiated objects, `PlatformAnalysis` receives the class itself and instantiates it on the remote server using the corresponding entry in `analyzers_args`.

```python
from idmtools.analysis.download_analyzer import DownloadAnalyzer
from myanalyzers import MyCSVAnalyzer

analysis = PlatformAnalysis(
    platform=platform,
    experiment_ids=['exp-id'],
    analyzers=[DownloadAnalyzer, MyCSVAnalyzer],   # classes, not instances
    analyzers_args=[
        {'filenames': ['output/InsetChart.json']},
        {'filenames': ['output/data.csv'], 'output_path': 'results'},
    ]
)
```

!!! warning
    Pass analyzer **classes**, not instances. `PlatformAnalysis` serializes and ships the analyzer source file to the remote worker, where it instantiates each class using the corresponding `analyzers_args` entry.

#### `analyzers_args`

**Type:** `List[dict] | None`  **Default:** `None`

A list of keyword-argument dictionaries, one per analyzer, passed to each analyzer's `__init__()` on the remote server.

- The list must be the same length as `analyzers`, or shorter (missing entries default to `{}`).
- If `None`, all analyzers are instantiated with no arguments (equivalent to `[{}, {}, ...]`).
- Entries can be `None` to use defaults for that specific analyzer.

```python
analyzers_args=[
    {'filenames': ['stderr.txt'], 'output_path': 'output'},  # for analyzer[0]
    None,                                                     # for analyzer[1] — use defaults
    {'output_path': 'tags_output'},                          # for analyzer[2]
]
```

#### `extra_args`

**Type:** `Dict[str, Any] | None`  **Default:** `None`

Extra keyword arguments forwarded directly to `AnalyzeManager.__init__()` on the remote server. These control how the remote analysis manager behaves. `PlatformAnalysis` validates each key against the `AnalyzeManager` signature at submission time and raises a `ValueError` for any unrecognised key.

The following table lists every supported key. The parameters `platform`, `ids`, and `analyzers` are excluded because `PlatformAnalysis` always sets them automatically from its own inputs.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `partial_analyze_ok` | `bool` | `False` | When `True`, skips simulations that are still running or failed and analyzes only those that succeeded. Set this when the experiment may not be fully complete. |
| `analyze_failed_items` | `bool` | `False` | When `True`, includes failed simulations in the analysis pool. Useful for collecting diagnostics or error outputs from simulations that did not finish successfully. |
| `max_workers` | `int` | CPU count | Maximum number of parallel worker processes on the remote server. Defaults to the platform's configured `max_workers`, then `[COMMON] max_workers` in `idmtools.ini`, then the remote machine's CPU count. |
| `max_items` | `int` | `None` | Limit analysis to at most this many simulations. Useful when developing or testing an analyzer remotely. Also implicitly enables `partial_analyze_ok`. |
| `working_dir` | `str` | remote cwd | Base directory for analyzer output on the remote worker. Each analyzer can override this individually via its own `working_dir`. |
| `exclude_ids` | `List[str]` | `[]` | Simulation IDs to skip, even if they are otherwise eligible for analysis. |
| `executor_type` | `str` | `'process'` | Worker pool type on the remote server: `'process'` (default, more efficient) or `'thread'` (required in some constrained environments). |
| `force_manager_working_directory` | `bool` | `False` | When `True`, forces all analyzers to write output to `working_dir`, ignoring each analyzer's own `working_dir` setting. |
| `verbose` | `bool` | `True` | Print analysis configuration and per-item timing on the remote worker. Note: `PlatformAnalysis.verbose` controls remote debug *logging*, while this key controls `AnalyzeManager`'s summary output. |
| `configuration` | `dict` | `{}` | Additional low-level configuration overrides passed to `AnalyzeManager`. Rarely needed in practice. |

```python
analysis = PlatformAnalysis(
    platform=platform,
    experiment_ids=['exp-id'],
    analyzers=[MyAnalyzer],
    analyzers_args=[{'filenames': ['output/result.json']}],
    extra_args=dict(
        partial_analyze_ok=True,       # proceed even if some simulations failed
        analyze_failed_items=False,    # skip failed simulations
        max_workers=8,                 # use 8 workers on the remote server
        max_items=50,                  # analyze at most 50 simulations
        exclude_ids=['sim-id-to-skip'],
        executor_type='process',       # use process pool (default)
    )
)
```

### All parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `platform` | `IPlatform` | **required** | An active COMPS platform instance. |
| `analyzers` | `List[Type[IAnalyzer]]` | **required** | Analyzer **classes** to run remotely. |
| `experiment_ids` | `List[str]` | `[]` | Experiment IDs to analyze. |
| `simulation_ids` | `List[str]` | `[]` | Individual simulation IDs to analyze. |
| `work_item_ids` | `List[str]` | `[]` | Work item IDs to analyze. |
| `analyzers_args` | `List[dict]` | `None` | Per-analyzer constructor kwargs for remote instantiation. |
| `analysis_name` | `str` | `'WorkItem Test'` | Name for the SSMT work item. |
| `tags` | `dict` | `None` | Tags to attach to the SSMT work item. |
| `additional_files` | `FileList \| AssetCollection \| List[str]` | `None` | Extra files to include alongside the analysis scripts on the remote worker. |
| `asset_collection_id` | `str` | `None` | ID of an existing asset collection to attach to the work item. |
| `asset_files` | `FileList \| AssetCollection \| List[str]` | `None` | Additional asset files to attach. |
| `wait_till_done` | `bool` | `True` | Block until the remote work item finishes. |
| `idmtools_config` | `str` | `None` | Path to a custom `idmtools.ini` to use on the remote server. |
| `pre_run_func` | `Callable` | `None` | A zero-argument function to execute on the remote server before analysis starts (e.g. to install packages). |
| `wrapper_shell_script` | `str` | `None` | Path to a shell script that wraps the remote analysis command. Mostly useful for development. |
| `verbose` | `bool` | `False` | Enable verbose logging on the remote worker. |
| `extra_args` | `Dict[str, Any]` | `None` | Extra kwargs forwarded to `AnalyzeManager` on the remote server. |

## Methods

| Method | Description |
|--------|-------------|
| `analyze(check_status=True)` | Submit the work item and (by default) wait for it to complete. |
| `get_work_item()` | Return the underlying `SSMTWorkItem` after `analyze()` has been called. |

## Examples

### Download files remotely

```python
from idmtools.analysis.download_analyzer import DownloadAnalyzer
from idmtools.core.platform_factory import Platform
from idmtools.analysis.platform_anaylsis import PlatformAnalysis

platform = Platform('CALCULON')

analysis = PlatformAnalysis(
    platform=platform,
    experiment_ids=["your-experiment-id"],
    analyzers=[DownloadAnalyzer],
    analyzers_args=[{'filenames': ["stderr.txt"], 'output_path': 'output'}],
    analysis_name="Download stderr",
)

analysis.analyze(check_status=True)
wi = analysis.get_work_item()
print(wi)
```

### Multiple analyzers with extra args

```python
from idmtools.analysis.csv_analyzer import CSVAnalyzer
from idmtools.analysis.tags_analyzer import TagsAnalyzer
from idmtools.core.platform_factory import Platform
from idmtools.analysis.platform_anaylsis import PlatformAnalysis

platform = Platform('CALCULON')

analysis = PlatformAnalysis(
    platform=platform,
    experiment_ids=["your-experiment-id"],
    analyzers=[CSVAnalyzer, TagsAnalyzer],
    analyzers_args=[
        {'filenames': ['output/data.csv'], 'output_path': 'csv_results'},
        {'output_path': 'tag_results'},
    ],
    analysis_name="Full Analysis",
    extra_args=dict(partial_analyze_ok=True)   # skip failed simulations
)

analysis.analyze(check_status=True)
```

### Custom analyzer from a local file

```python
from myproject.analyzers import MyCustomAnalyzer
from idmtools.core.platform_factory import Platform
from idmtools.analysis.platform_anaylsis import PlatformAnalysis

platform = Platform('CALCULON')

analysis = PlatformAnalysis(
    platform=platform,
    experiment_ids=["your-experiment-id"],
    analyzers=[MyCustomAnalyzer],
    analyzers_args=[{'filenames': ['output/result.json'], 'threshold': 0.5}],
    analysis_name="Custom Analysis",
    verbose=True   # turn on debug logging on the remote worker
)

analysis.analyze(check_status=True)
```

!!! tip
    The source file of each analyzer class is automatically packaged and sent to the remote worker. You do not need to manually add them to `additional_files`.

## How it works internally

1. `PlatformAnalysis` serializes analyzer constructor arguments into a pickle file (`analyzer_args.pkl`)
2. The analyzer source files are added to the work item's transient assets
3. A bootstrap script (`platform_analysis_bootstrap.py`) is included as the entry point
4. An `SSMTWorkItem` is created with all assets and submitted to COMPS
5. On the remote worker, the bootstrap script deserializes the args, instantiates the analyzers, and runs `AnalyzeManager`

## Next steps

- [AnalyzeManager](analyze-manager.md) — Run analysis locally
- [Analyzers](analyzers.md) — Write custom analyzer logic
- [COMPS platform](../platforms/comps.md) — Configure and use the COMPS platform
