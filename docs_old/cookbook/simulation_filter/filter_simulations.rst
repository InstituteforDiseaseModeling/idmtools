Filtering Simulations
=====================

This example demonstrates how to filter simulations using criteria like tags, status, entity_type etc.

It supports two approaches:

1. Filtering directly from an `Experiment` or `Suite` with get_simulations_by_tags method
2. Filtering via the platform's `filter_simulations_by_tags` method

Supported Tag Filters
---------------------
- Exact matches (e.g., ``"Reporting_Rate": 0.01``)
- String vs numeric equivalence
- Callable filters (e.g., lambdas like ``lambda v: 2 <= v <= 10``)

The tag values are normalized using ``TagValue`` to ensure type-safe comparisons behind the scenes.

Usage
-----

.. code-block:: python

    from idmtools.core import ItemType
    from idmtools.core.platform_factory import Platform
    from idmtools.entities.simulation import Simulation

    platform = Platform('Calculon')

    # Load experiment
    experiment = platform.get_item("4721ac6b-9344-ef11-aa15-9440c9be2c51", ItemType.EXPERIMENT)

    # Filter simulations with different representations of tag values
    filter_simulation_ids = experiment.get_simulations_by_tags(
        tags={"__sample_index__": lambda v: 2 <= v <= 10, "Reporting_Rate": "0.01"})
    filter_simulation_ids1 = experiment.get_simulations_by_tags(
        tags={"__sample_index__": lambda v: 2 <= v <= 10, "Reporting_Rate": 0.01})
    filter_simulation_ids2 = experiment.get_simulations_by_tags(
        tags={"__sample_index__": lambda v: "2" <= v <= 10, "Reporting_Rate": 0.01})

    # Alternative: Filter via platform method
    filter_simulation_ids_p = platform.filter_simulations_by_tags(
        experiment.id, item_type=ItemType.EXPERIMENT,
        tags={"__sample_index__": lambda v: 2 <= v <= 10, "Reporting_Rate": 0.01})

    assert len(filter_simulation_ids) == 3
    assert len(filter_simulation_ids1) == 3
    assert len(filter_simulation_ids2) == 3

    # Retrieve Simulation objects instead of just IDs
    filter_simulations = experiment.get_simulations_by_tags(
        tags={"__sample_index__": lambda v: 2 <= v <= 10, "Reporting_Rate": "0.01"},
        entity_type=True)

    for sim in filter_simulations:
        assert isinstance(sim, Simulation)
        print(sim.tags)

Suite-Level Filtering
---------------------

.. code-block:: python

    suite = platform.get_item("5230d6ef-9144-ef11-aa15-9440c9be2c51", item_type=ItemType.SUITE, force=True)

    # Filter across all experiments in the suite
    filter_suite_simulations = suite.get_simulations_by_tags(
        tags={"__sample_index__": lambda v: "2" <= v <= 10, "Reporting_Rate": 0.01},
        entity_type=True)

    assert len(filter_suite_simulations) == 5
    for exp_id, sims in filter_suite_simulations.items():
        assert len(sims) >= 3
        for sim in sims:
            print(sim.tags)

    # Alternative using platform method
    filter_suite_simulations_p = platform.filter_simulations_by_tags(
        suite.id, item_type=ItemType.SUITE,
        tags={"__sample_index__": lambda v: "2" <= v <= 10, "Reporting_Rate": 0.01},
        entity_type=True)

    assert filter_suite_simulations == filter_suite_simulations_p

Notes
-----
- If entity_type=True, it will return matched simulations instead of simulation ids.
- The use of `lambda` filters enables flexible querying for ranges and type coercion.
- This example assumes the simulations were tagged during sweep or post-processing stages.
- This filter feature also works in Container Platform.
