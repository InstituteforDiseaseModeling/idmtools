# Analyzers (IAnalyzer)

Analyzers define *how* to extract and aggregate data from simulation outputs. Every analyzer extends `IAnalyzer`, which provides the map-reduce interface.

## What Is an Analyzer?

An `IAnalyzer` is a class you implement with two core methods:

- **`map(data, simulation)`** — called once per simulation; receives the simulation's output files and returns any Python object
- **`reduce(all_data)`** — called once after all simulations are mapped; receives `{simulation: map_result}` and produces the final output (CSV, plots, etc.)

You can optionally override:

- **`initialize()`** — called once before mapping begins; use it to create output directories or load shared resources
- **`filter(simulation)`** — return `True` to include a simulation, `False` to skip it
- **`destroy()`** — called after `reduce()` completes; use it for cleanup

## Constructor Parameters

```python
IAnalyzer(uid=None, working_dir=None, parse=True, filenames=None)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `uid` | `str` | class name | Unique identifier for this analyzer instance. Auto-set to the class name if omitted. Must be unique when multiple analyzers are used together. |
| `working_dir` | `str` | `None` | Directory where analyzer output is written. Falls back to `AnalyzeManager.working_dir` if not set. |
| `parse` | `bool` | `True` | When `True`, idmtools parses output files into Python objects (e.g. JSON → dict). When `False`, you receive raw `bytes` and must parse them yourself — useful for custom binary formats or CSV files you want to read with pandas. |
| `filenames` | `List[str]` | `[]` | Paths of output files to retrieve from each simulation, relative to the simulation root (e.g. `"output/result.json"`). Only these files are downloaded. |

## Basic Custom Analyzer

```python
from typing import Dict, Any
from idmtools.entities import IAnalyzer

class MyAnalyzer(IAnalyzer):
    def __init__(self):
        super().__init__(filenames=["output/result.json"])

    def map(self, data: Dict[str, Any], simulation) -> Any:
        # data is keyed by filename; value is a parsed object (dict for JSON)
        return data[self.filenames[0]]

    def reduce(self, all_data: Dict) -> None:
        for simulation, result in all_data.items():
            print(f"Simulation {simulation.id}: {result}")
```

## Filtering Simulations

Override `filter()` to skip simulations that don't meet your criteria:

```python
class FilteredAnalyzer(IAnalyzer):
    def __init__(self):
        super().__init__(filenames=["config.json"])

    def filter(self, simulation) -> bool:
        # only analyze simulations where tag "b" > 5
        return int(simulation.tags.get("b", 0)) > 5

    def map(self, data: Dict[str, Any], simulation):
        return data[self.filenames[0]]

    def reduce(self, all_data: Dict):
        for simulation, result in all_data.items():
            print(simulation.id, result)
```

## Raw File Access (parse=False)

Set `parse=False` to receive raw bytes and handle parsing yourself — useful for CSV files with non-standard formatting:

```python
import os
from io import BytesIO
from typing import Dict
import pandas as pd
from idmtools.entities import IAnalyzer

class MyCSVAnalyzer(IAnalyzer):
    def __init__(self, filenames, output_path="output"):
        # parse=False delivers raw bytes instead of a parsed object
        super().__init__(parse=False, filenames=filenames)
        self.output_path = output_path

    def initialize(self):
        # called once before map(); create output directories here
        self.output_path = os.path.join(self.working_dir, self.output_path)
        os.makedirs(self.output_path, exist_ok=True)

    def map(self, data, simulation) -> pd.DataFrame:
        # data[filename] is raw bytes when parse=False
        return pd.read_csv(BytesIO(data[self.filenames[0]]), skiprows=0, header=None)

    def reduce(self, all_data: Dict):
        results = pd.concat(
            list(all_data.values()), axis=0,
            keys=[str(k.id) for k in all_data.keys()],
            names=['SimId']
        )
        results.index = results.index.droplevel(1)
        results = results.rename(columns={0: "Age", 1: "City"})

        first_sim = list(all_data.keys())[0]
        exp_id = first_sim.experiment.id
        output_folder = os.path.join(self.output_path, exp_id)
        os.makedirs(output_folder, exist_ok=True)
        results.to_csv(os.path.join(output_folder, self.__class__.__name__ + '.csv'))
```

## Built-In Analyzers

idmtools ships several ready-to-use analyzers:

### DownloadAnalyzer

Downloads the specified files from each simulation into the local working directory without further processing:

```python
from idmtools.analysis.download_analyzer import DownloadAnalyzer

analyzer = DownloadAnalyzer(filenames=['output/InsetChart.json'])
```

You can also subclass it:

```python
class InsetDownloader(DownloadAnalyzer):
    filenames = ['output/InsetChart.json']
```

### CSVAnalyzer

Reads CSV output files and concatenates them across all simulations into a single CSV keyed by simulation ID:

```python
from idmtools.analysis.csv_analyzer import CSVAnalyzer

# filenames: list of CSV files to retrieve from each simulation
analyzer = CSVAnalyzer(filenames=['output/data.csv'], output_path='results')
```

### TagsAnalyzer

Collects all simulation tags into a single CSV file — useful for documenting what parameters were used:

```python
from idmtools.analysis.tags_analyzer import TagsAnalyzer

analyzer = TagsAnalyzer(output_path='output_tags')
```

### AddAnalyzer

Reads a text-based output file and prints or accumulates its contents across simulations:

```python
from idmtools.analysis.add_analyzer import AddAnalyzer

analyzer = AddAnalyzer(filenames=['stdout.txt'])
```

## Next Steps

- [AnalyzeManager](analyze-manager.md) — Run your analyzers locally
- [PlatformAnalysis](platform-analysis.md) — Run your analyzers remotely on COMPS
