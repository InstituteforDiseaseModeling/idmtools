"""
Example: Filtering Simulations by Tags from Experiment and Suite Levels

This example demonstrates how to filter simulations using tag-based criteria.
It shows both:
    1. Filtering simulations directly from an Experiment or Suite
    2. Filtering via the platform's `filter_simulations_by_tags` method

Supported tag filters:
    - Exact matches (e.g., "Reporting_Rate": 0.01)
    - String vs numeric equivalence
    - Callable filters (e.g., lambdas like `lambda v: 2 <= v <= 10`)

Note: The tag values are normalized using `TagValue` to ensure type-safe comparison behind the scene.
"""
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities.simulation import Simulation

# Load platform and experiment
platform = Platform('Calculon')

"""
Experiment-level Filtering
---------------------------
"""
experiment = platform.get_item("4721ac6b-9344-ef11-aa15-9440c9be2c51", ItemType.EXPERIMENT)

# Filter simulations using different representations of tag values
filter_simulation_ids = experiment.simulations_with_tags(
    tags={"__sample_index__": lambda v: 2 <= v <= 10, "Reporting_Rate": "0.01"})
filter_simulation_ids1 = experiment.simulations_with_tags(
    tags={"__sample_index__": lambda v: 2 <= v <= 10, "Reporting_Rate": 0.01})
filter_simulation_ids2 = experiment.simulations_with_tags(
    tags={"__sample_index__": lambda v: "2" <= v <= 10, "Reporting_Rate": 0.01})

# Alternative: Filter via platform method
filter_simulation_ids_p = platform.filter_simulations_by_tags(
    experiment.id, item_type=ItemType.EXPERIMENT,
    tags={"__sample_index__": lambda v: 2 <= v <= 10, "Reporting_Rate": 0.01})

# Validation
assert len(filter_simulation_ids) == 3
assert len(filter_simulation_ids1) == 3
assert len(filter_simulation_ids2) == 3

# Get simulation entities (instead of IDs) using entity_type=True
filter_simulations = experiment.simulations_with_tags(
    tags={"__sample_index__": lambda v: 2 <= v <= 10, "Reporting_Rate": "0.01"},
    entity_type=True)

count = 0
for sim in filter_simulations:
    assert isinstance(sim, Simulation)
    count += 1
    print(sim.tags)

assert count == 3

"""
Suite-level Filtering
---------------------
"""

# Load suite and filter simulations across its experiments
suite = platform.get_item("5230d6ef-9144-ef11-aa15-9440c9be2c51", item_type=ItemType.SUITE, force=True)
filter_suite_simulations = suite.simulations_with_tags(
    tags={"__sample_index__": lambda v: "2" <= v <= 10, "Reporting_Rate": 0.01},
    entity_type=True)

# Validate structure and results
assert len(filter_suite_simulations) == 5  # 5 experiments matched
for exp_id, sims in filter_suite_simulations.items():
    assert len(sims) >= 3
    for sim in sims:
        print(sim.tags)

# Alternative: Use platform-level method for suite
filter_suite_simulations_p = platform.filter_simulations_by_tags(
    suite.id, item_type=ItemType.SUITE,
    tags={"__sample_index__": lambda v: "2" <= v <= 10, "Reporting_Rate": 0.01},
    entity_type=True)

# Ensure both methods return the same results
assert filter_suite_simulations == filter_suite_simulations_p
