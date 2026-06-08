# Filtering simulations by tags

Filter simulations from a completed experiment or suite using tag-based criteria.

## Overview

After running an experiment, you can retrieve specific simulations by filtering on their tags. Filters support:

- `Exact matches` — `"beta": 0.5`
- `String/numeric equivalence` — `"beta": "0.5"` matches `0.5`
- `Callable filters` — `lambda v: 1 <= v <= 5` for range queries

There are two ways to filter:

- `experiment.get_simulations_by_tags()` — filter from the experiment object
- `platform.filter_simulations_by_tags()` — filter via the platform directly

---

## Experiment-level filtering

```python
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities.simulation import Simulation

platform = Platform("Container", job_directory="DEST")

experiment = platform.get_item("your-experiment-id", ItemType.EXPERIMENT)

# Filter by exact tag value
filter_ids = experiment.get_simulations_by_tags(
    tags={"beta": 0.5, "sim_tag": "test_tag"})

# Filter by range using a lambda
filter_ids2 = experiment.get_simulations_by_tags(
    tags={"a": lambda v: 1 <= v <= 5, "sim_tag": "test_tag"})

# Alternative: filter via the platform method
filter_ids_p = platform.filter_simulations_by_tags(
    experiment.id, item_type=ItemType.EXPERIMENT,
    tags={"a": lambda v: 1 <= v <= 5, "sim_tag": "test_tag"})

print(f"Matched {len(filter_ids2)} simulations")
```

## Return simulation objects

By default, filtering returns simulation IDs. Use `entity_type=True` to get full `Simulation` objects:

```python
# Get simulation entities instead of IDs
simulations = experiment.get_simulations_by_tags(
    tags={"a": lambda v: 1 <= v <= 5, "sim_tag": "test_tag"},
    entity_type=True)

for sim in simulations:
    print(sim.tags)
```

---

## Suite-level filtering

Filter simulations across all experiments in a suite:

```python
# Get suite from experiment
suite = experiment.suite

# Filter across all experiments in the suite
# Returns a dict of {experiment_id: [simulations]}
suite_results = suite.get_simulations_by_tags(
    tags={"a": lambda v: 1 <= v <= 5, "sim_tag": "test_tag"},
    entity_type=True)

for exp_id, sims in suite_results.items():
    print(f"Experiment {exp_id}: {len(sims)} matching simulations")
    for sim in sims:
        print(sim.tags)

# Alternative: filter via platform method
suite_results_p = platform.filter_simulations_by_tags(
    suite.id, item_type=ItemType.SUITE,
    tags={"a": lambda v: 1 <= v <= 5, "sim_tag": "test_tag"},
    entity_type=True)
```

---

## Next steps

- [Parameter Sweeps](parameter-sweeps.md) - Tag simulations during sweeps for easy filtering
- [Analyzing Results](../data-analysis/index.md) - Analyze filtered simulation outputs
