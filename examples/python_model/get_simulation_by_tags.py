"""
Example: Filtering simulations from an experiment using flexible tag-based conditions.

This example demonstrates how to use `simulations_with_tags()` with both:
- Static tag values (e.g., "Coverage": 0.8)
- Range tag filters using lambda expressions (e.g., "Run_Number": lambda v: 2 <= v <= 10)

The internal system normalizes tag values (e.g., "0.8" vs 0.8) to ensure consistent matching.
"""
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities.simulation import Simulation

platform = Platform('Calculon')
experiment = platform.get_item("3966b90b-364c-f011-aa22-b88303911bc1", ItemType.EXPERIMENT)
# Below 3 cases should all match to the same simulation ids
filter_simulation_ids = experiment.simulations_with_tags(tags={"Run_Number": lambda v: 2 <= v <= 10, "Coverage": "0.8"})
filter_simulation_ids1 = experiment.simulations_with_tags(tags={"Run_Number": lambda v: 2 <= v <= 10, "Coverage": 0.8})
filter_simulation_ids2 = experiment.simulations_with_tags(tags={"Run_Number": lambda v: "2" <= v <= 10, "Coverage": 0.8})

assert len(filter_simulation_ids) == 9
assert len(filter_simulation_ids1) == 9
assert len(filter_simulation_ids2) == 9

# Below call with entity_type=True will return matched simulation objects. Total count should be the same as above cases
filter_simulations = experiment.simulations_with_tags(tags={"Run_Number": lambda v: 2 <= v <= 10, "Coverage": "0.8"}, entity_type=True)
count = 0
for sim in filter_simulations:
    assert isinstance(sim, Simulation)
    count += 1
    print(sim.tags)
assert count == 9
