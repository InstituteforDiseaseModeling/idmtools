# Analyzing Results

Learn how to analyze simulation outputs using idmtools analyzers.

## Overview

Analyzers extract and aggregate data from simulation outputs using a **map-reduce** pattern:

- Map — process each simulation's output individually 
- Reduce — aggregate results across all simulations

There are two ways to run analyzers:

- AnalyzeManager — runs analyzers locally against an experiment by ID
- PlatformAnalysis — runs analyzers as a remote work item on the platform (SSMT), useful when the analysis environment or data needs to stay on the cluster

## Basic Pattern: Custom IAnalyzer

```python
from typing import Dict, Any
from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities import IAnalyzer

class ExampleAnalyzer(IAnalyzer):
    def __init__(self, uid=None, working_dir=None, parse=True):
        # filenames: list of output files to retrieve from each simulation
        super().__init__(uid, working_dir, parse, filenames=["output/result.json"])

    def map(self, data, simulation):
        # data is a dict keyed by filename; return whatever you need per simulation
        result = data[self.filenames[0]]
        return result

    def reduce(self, all_data):
        # all_data is a dict of {simulation: map_result}
        for simulation, result in all_data.items():
            print(simulation)
            print(result)

if __name__ == "__main__":
    with Platform('CALCULON') as platform:
        experiment_id = 'your-experiment-id'
        manager = AnalyzeManager(
            ids=[(experiment_id, ItemType.EXPERIMENT)],
            analyzers=[ExampleAnalyzer()]
        )
        manager.analyze()
```

## Filtering Simulations

Use `filter()` to analyze only simulations meeting certain criteria:

```python
class ExampleAnalyzer2(IAnalyzer):
    def __init__(self, uid=None, working_dir=None, parse=True):
        super().__init__(uid, working_dir, parse, filenames=["config.json"])

    def filter(self, simulation) -> bool:
        # only analyze simulations where tag "b" > 5
        return int(simulation.tags.get("b")) > 5

    def map(self, data: Dict[str, Any], simulation):
        result = data[self.filenames[0]]
        return result

    def reduce(self, all_data: Dict):
        for simulation, result in all_data.items():
            print(simulation)
            print(result)
```

## Multiple Analyzers

Run multiple analyzers in a single `AnalyzeManager`:

```python
if __name__ == "__main__":
    with Platform('CALCULON') as platform:
        experiment_id = 'your-experiment-id'

        # Pass all analyzers at construction time
        analyzers = [ExampleAnalyzer(), ExampleAnalyzer2()]
        manager = AnalyzeManager(ids=[(experiment_id, ItemType.EXPERIMENT)], analyzers=analyzers)
        manager.analyze()

        # Or add analyzers individually before calling analyze()
        manager2 = AnalyzeManager(ids=[(experiment_id, ItemType.EXPERIMENT)])
        manager2.add_analyzer(ExampleAnalyzer())
        manager2.add_analyzer(ExampleAnalyzer2())
        manager2.analyze()
```

## Custom CSV Analyzer (parse=False)

Use `parse=False` to handle file parsing yourself:

```python
import os
from io import BytesIO
from typing import Dict
import pandas as pd
from idmtools.entities import IAnalyzer

class MyCSVAnalyzer(IAnalyzer):
    def __init__(self, filenames, parse=True, output_path="output"):
        # parse=False tells idmtools to deliver raw bytes instead of a parsed object
        super().__init__(parse=parse, filenames=filenames)
        self.output_path = output_path

    def initialize(self):
        # called once before map(); good place to create output directories
        self.output_path = os.path.join(self.working_dir, self.output_path)
        os.makedirs(self.output_path, exist_ok=True)

    def map(self, data, simulation) -> pd.DataFrame:
        # data[filename] is raw bytes when parse=False; read manually
        selected_df = pd.read_csv(BytesIO(data[self.filenames[0]]), skiprows=0, header=None)
        return selected_df

    def reduce(self, all_data: Dict):
        # combine all simulation dataframes, indexed by simulation ID
        results = pd.concat(
            list(all_data.values()), axis=0,
            keys=[str(k.id) for k in all_data.keys()],
            names=['SimId']
        )
        results.index = results.index.droplevel(1)
        results = results.rename(columns={0: "Age", 1: "City"})

        # write results under a folder named by experiment ID
        first_sim = list(all_data.keys())[0]
        exp_id = first_sim.experiment.id
        output_folder = os.path.join(self.output_path, exp_id)
        os.makedirs(output_folder, exist_ok=True)
        results.to_csv(os.path.join(output_folder, self.__class__.__name__ + '.csv'))

if __name__ == '__main__':
    with Platform('CALCULON') as platform:
        analyzers = [MyCSVAnalyzer(filenames=['output/b.csv'], parse=False)]
        manager = AnalyzeManager(
            partial_analyze_ok=True,  # continue even if some simulations failed
            ids=[('your-experiment-id', ItemType.EXPERIMENT)],
            analyzers=analyzers
        )
        manager.analyze()
```

## PlatformAnalysis (SSMT)

Run analysis as a remote work item on COMPS:

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
    analysis_name="My Analysis",
    extra_args=dict(partial_analyze_ok=True) 
)

analysis.analyze(check_status=True)
wi = analysis.get_work_item()  
print(wi)
```

## Next Steps

- [Parameter Sweeps](../tutorials/parameter-sweeps.md) - Run sweeps to analyze
- [Platforms](../platforms/index.md) - Platform-specific analysis details
