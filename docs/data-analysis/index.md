# Data analysis

idmtools provides a **map-reduce** framework for analyzing simulation outputs after your experiment has finished running.

## Overview

The analysis pipeline consists of three components:

| Component | Description |
|-----------|-------------|
| [IAnalyzer](analyzers.md) | Base class you implement to define *how* to process and aggregate simulation outputs |
| [AnalyzeManager](analyze-manager.md) | Runs analyzers **locally** against one or more experiments, suites, or simulations |
| [PlatformAnalysis](platform-analysis.md) | Runs analyzers **remotely** as an SSMT work item on COMPS — keeps data on the cluster and avoids large transfers |

## How it works

Analysis follows a map-reduce pattern:

```
Simulations ──► map()   ──► per-simulation result
                              │
                              ▼
                         reduce()  ──► aggregate output (CSV, plots, etc.)
```

1. **map** — called once per simulation; receives the simulation's output files and returns any Python object
2. **reduce** — called once after all simulations are mapped; receives `{simulation: map_result}` and produces the final output

## Quick example

```python
from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities import IAnalyzer

class MyAnalyzer(IAnalyzer):
    def __init__(self):
        super().__init__(filenames=["output/result.json"])

    def map(self, data, simulation):
        return data[self.filenames[0]]

    def reduce(self, all_data):
        for sim, result in all_data.items():
            print(sim.id, result)

with Platform('CALCULON') as platform:
    manager = AnalyzeManager(
        ids=[('your-experiment-id', ItemType.EXPERIMENT)],
        analyzers=[MyAnalyzer()]
    )
    manager.analyze()
```

## Choosing between AnalyzeManager and PlatformAnalysis

| | AnalyzeManager | PlatformAnalysis |
|---|---|---|
| **Where it runs** | Your local machine | Remote SSMT worker on COMPS |
| **Data transfer** | Downloads output files locally | Files stay on the cluster |
| **Best for** | Development, small datasets | Large datasets, production workflows |
| **Platform required** | Any idmtools platform | COMPS only |

## In this section

- [Analyzers (IAnalyzer)](analyzers.md) — Define custom analysis logic and use built-in analyzers
- [AnalyzeManager](analyze-manager.md) — Run analysis locally with full parameter reference
- [PlatformAnalysis](platform-analysis.md) — Run analysis remotely on COMPS via SSMT