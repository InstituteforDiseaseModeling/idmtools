"""
Example: Filtering Simulations by Tags from Experiment and Suite Levels in Container Platform

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

import os
import sys

from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities.simulation import Simulation

sys.path.insert(0, os.path.dirname(__file__))
from create_experiment import create_experiment

platform = Platform("Container", job_directory="DEST")
#platform = Platform("Container", job_directory="DEST", use_new_layout=False)
experiment = create_experiment(platform)
#experiment = platform.get_item("8e622977-2034-4515-ad8b-1070664b1e3f", ItemType.EXPERIMENT)
assert experiment.succeeded == True

"""
Experiment-level Filtering
---------------------------
"""

# Filter simulations using different representations of tag values
filter_simulation_ids = experiment.get_simulations_by_tags(
    tags={"a": lambda v: 1 <= v <= 2, "sim_tag": "test_tag"})
filter_simulation_ids1 = experiment.get_simulations_by_tags(
    tags={"a": lambda v: "1" <= v <= 2, "sim_tag": "test_tag"})
filter_simulation_ids2 = experiment.get_simulations_by_tags(
    tags={"a": lambda v: 1 <= v <= "2", "sim_tag": "test_tag"})

# Alternative: Filter via platform method
filter_simulation_ids_p = platform.filter_simulations_by_tags(
    experiment.id, item_type=ItemType.EXPERIMENT,
    tags={"a": lambda v: 1 <= v <= "2", "sim_tag": "test_tag"})

# Validation there are 40 simulations matched (out of 60)
assert len(filter_simulation_ids) == 10
assert len(filter_simulation_ids1) == 10
assert len(filter_simulation_ids2) == 10

# Get simulation entities (instead of IDs) using entity_type=True
filter_simulations = experiment.get_simulations_by_tags(
    tags={"a": lambda v: 1 <= v <= "2", "sim_tag": "test_tag"},
    entity_type=True)

count = 0
for sim in filter_simulations:
    assert isinstance(sim, Simulation)
    count += 1
    print(sim.tags)

assert count == 10

"""
Suite-level Filtering
---------------------
"""

# Load suite and filter simulations across its experiments
suite = experiment.suite
filter_suite_simulations = suite.get_simulations_by_tags(
    tags={"a": lambda v: 1 <= v <= 2, "sim_tag": "test_tag"}, entity_type=True)

print("another test")
# Validate structure and results
assert len(filter_suite_simulations) == 1  # 1 experiment matched
for exp_id, sims in filter_suite_simulations.items():
    assert len(sims) >= 10
    for sim in sims:
        print(sim.tags)

# Alternative: Use platform-level method for suite
filter_suite_simulations_p = platform.filter_simulations_by_tags(
    suite.id, item_type=ItemType.SUITE,
    tags={"a": lambda v: 1 <= v <= 2, "sim_tag": "test_tag"}, entity_type=True)

# Ensure both methods return the same results
assert len(filter_suite_simulations) == len(filter_suite_simulations_p) == 1
assert len(filter_suite_simulations[experiment.id]) == len(filter_suite_simulations_p[experiment.id]) == 10
