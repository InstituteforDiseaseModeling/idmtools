# AnalyzeManager

`AnalyzeManager` is the local analysis driver. It retrieves simulation output files from the platform, runs each analyzer's `map()` in parallel, then calls each analyzer's `reduce()` to produce the final results — all on your local machine.

## What can AnalyzeManager do?

- Run one or more [IAnalyzer](analyzers.md) instances against experiments, suites, or individual simulations
- Process simulations in parallel using a configurable worker pool (process-based or thread-based)
- Skip failed or in-progress simulations, or explicitly include them
- Limit the number of simulations processed — handy when developing and testing an analyzer
- Exclude specific simulation IDs from analysis

## Import

```python
from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
```

## Constructor parameters

```python
AnalyzeManager(
    platform=None,
    ids=None,
    analyzers=None,
    working_dir=None,
    partial_analyze_ok=False,
    analyze_failed_items=False,
    max_workers=None,
    max_items=None,
    verbose=True,
    exclude_ids=None,
    executor_type='process',
    force_manager_working_directory=False,
    configuration=None,
)
```

### Key parameters

#### `analyzers`

**Type:** `List[IAnalyzer]`  **Default:** `[]`

The list of analyzer instances to run. Each analyzer must be an instance of a class that extends [`IAnalyzer`](analyzers.md). You can pass analyzers at construction time or add them later with `add_analyzer()`.

```python
manager = AnalyzeManager(
    ids=[('exp-id', ItemType.EXPERIMENT)],
    analyzers=[MyAnalyzer(), AnotherAnalyzer()]
)

# Or add them one by one before calling analyze()
manager = AnalyzeManager(ids=[('exp-id', ItemType.EXPERIMENT)])
manager.add_analyzer(MyAnalyzer())
manager.add_analyzer(AnotherAnalyzer())
```

#### `partial_analyze_ok`

**Type:** `bool`  **Default:** `False`

Controls whether analysis proceeds when some simulations are not in a `Succeeded` state (e.g., still running, failed, or queued).

- `False` (default) — raises `ItemsNotReady` if any simulation is not ready; all simulations must be succeeded
- `True` — skips any non-ready simulations and analyzes only those that are ready

Use `partial_analyze_ok=True` when you want to analyze a partial set of results from a still-running experiment, or when a subset of simulations failed and you want results from the rest.

```python
manager = AnalyzeManager(
    ids=[('exp-id', ItemType.EXPERIMENT)],
    analyzers=[MyAnalyzer()],
    partial_analyze_ok=True   # analyze succeeded simulations even if some failed
)
```

!!! note
    Setting `max_items` automatically enables `partial_analyze_ok`.

#### `analyze_failed_items`

**Type:** `bool`  **Default:** `False`

When `True`, failed simulations are included in the analysis pool (subject to `partial_analyze_ok` rules). This is useful when you want to aggregate diagnostics or error outputs from simulations that did not complete successfully.

```python
manager = AnalyzeManager(
    ids=[('exp-id', ItemType.EXPERIMENT)],
    analyzers=[ErrorDiagnosticAnalyzer()],
    partial_analyze_ok=True,
    analyze_failed_items=True   # include failed simulations
)
```

#### `max_workers`

**Type:** `int | None`  **Default:** `None`

Sets the maximum number of parallel worker processes (or threads) used during the `map()` phase.

Resolution order when `max_workers` is `None`:
1. `max_workers` in the platform's configuration block (`idmtools.ini`)
2. `max_workers` in the `[COMMON]` configuration block
3. `os.cpu_count()` (number of logical CPU cores on the local machine)

```python
manager = AnalyzeManager(
    ids=[('exp-id', ItemType.EXPERIMENT)],
    analyzers=[MyAnalyzer()],
    max_workers=4   # use exactly 4 worker processes
)
```

!!! tip
    On machines with many cores, leave `max_workers=None` to use all available CPUs. Set it explicitly if you need to limit resource usage or avoid memory pressure.

### All parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `platform` | `IPlatform` | `None` | Platform to use. If omitted, uses the current platform context (`with Platform(...) as platform`). |
| `ids` | `List[Tuple[str, ItemType]]` | `None` | List of `(id, ItemType)` pairs identifying the experiments, suites, or simulations to analyze. |
| `analyzers` | `List[IAnalyzer]` | `[]` | Analyzer instances to run. |
| `working_dir` | `str` | `os.getcwd()` | Base directory for analyzer output. Each analyzer can override this individually. |
| `partial_analyze_ok` | `bool` | `False` | When `True`, analyze only ready simulations; skip those that are still running or failed. |
| `analyze_failed_items` | `bool` | `False` | When `True`, include failed simulations in the analysis. |
| `max_workers` | `int` | `None` | Number of parallel workers. Defaults to CPU count if not set in configuration. |
| `max_items` | `int` | `None` | Limit analysis to at most this many simulations. Useful during analyzer development. Also enables `partial_analyze_ok`. |
| `verbose` | `bool` | `True` | Print analysis configuration and timing information. |
| `exclude_ids` | `List[str]` | `[]` | Simulation IDs to skip, even if they are otherwise eligible. |
| `executor_type` | `str` | `'process'` | Worker pool type: `'process'` (default, more efficient) or `'thread'` (required in some environments such as Jupyter notebooks). |
| `force_manager_working_directory` | `bool` | `False` | When `True`, forces all analyzers to write output to `working_dir` regardless of their own `working_dir` setting. |
| `configuration` | `dict` | `{}` | Additional configuration overrides. |

## Methods

| Method | Description |
|--------|-------------|
| `analyze()` | Run the full map-reduce pipeline. Returns `True` on success, `False` on failure. |
| `add_analyzer(analyzer)` | Add an analyzer before calling `analyze()`. |
| `add_item(item)` | Add an additional item for analysis after construction. |

## Examples

### Single analyzer

```python
from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities import IAnalyzer

class ExampleAnalyzer(IAnalyzer):
    def __init__(self):
        super().__init__(filenames=["output/result.json"])

    def map(self, data, simulation):
        return data[self.filenames[0]]

    def reduce(self, all_data):
        for simulation, result in all_data.items():
            print(simulation.id, result)

if __name__ == "__main__":
    with Platform('CALCULON') as platform:
        manager = AnalyzeManager(
            ids=[('your-experiment-id', ItemType.EXPERIMENT)],
            analyzers=[ExampleAnalyzer()]
        )
        manager.analyze()
```

### Multiple analyzers

```python
if __name__ == "__main__":
    with Platform('CALCULON') as platform:
        experiment_id = 'your-experiment-id'

        # Pass all analyzers at construction time
        manager = AnalyzeManager(
            ids=[(experiment_id, ItemType.EXPERIMENT)],
            analyzers=[ExampleAnalyzer(), FilteredAnalyzer()]
        )
        manager.analyze()
```

### Partial analysis (some simulations may not be ready)

```python
from idmtools.analysis.csv_analyzer import CSVAnalyzer

if __name__ == '__main__':
    with Platform('CALCULON') as platform:
        manager = AnalyzeManager(
            ids=[('your-experiment-id', ItemType.EXPERIMENT)],
            analyzers=[CSVAnalyzer(filenames=['output/data.csv'])],
            partial_analyze_ok=True   # skip failed/pending simulations
        )
        manager.analyze()
```

### Include failed simulations

```python
if __name__ == '__main__':
    with Platform('CALCULON') as platform:
        manager = AnalyzeManager(
            ids=[('your-experiment-id', ItemType.EXPERIMENT)],
            analyzers=[MyDiagnosticAnalyzer()],
            partial_analyze_ok=True,
            analyze_failed_items=True   # also analyze failed simulations
        )
        manager.analyze()
```

### Limit workers (e.g. for notebooks or low-memory machines)

```python
if __name__ == '__main__':
    with Platform('CALCULON') as platform:
        manager = AnalyzeManager(
            ids=[('your-experiment-id', ItemType.EXPERIMENT)],
            analyzers=[MyAnalyzer()],
            max_workers=2,
            executor_type='thread'   # use threads instead of processes
        )
        manager.analyze()
```

## Next steps

- [PlatformAnalysis](platform-analysis.md) — Run analysis remotely on COMPS
- [Analyzers](analyzers.md) — Write custom analyzer logic
