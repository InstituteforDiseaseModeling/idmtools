======================================
Running parameter sweeps with |EMOD_s|
======================================

When running parameter sweeps with |EMOD_s|, you use the :py:class:`~emodpy.emod_task.EMODTask` class for setting the sweep parameters and passing them to the :py:class:`~idmtools.builders.simulation_builder.SimulationBuilder` class using the add_sweep_definition method.

In addition to the parameters for sweeping, you must also set the "Run_Number" parameter. This determines the seed for the random number generator. This is particularly important with |EMOD_s| in order to explore the stochastic nature of the model. Otherwise, if "Run_Number" is not changed then each simulation will result in the same output.

The following Python code excerpt shows an example::

    # Create TemplatedSimulations with task
    ts = TemplatedSimulations(base_task=task)

    # Create SimulationBuilder
    builder = SimulationBuilder()

    # Add sweep parameter to builder
    builder.add_sweep_definition(EMODTask.set_parameter_partial("Run_Number"), range(num_seeds))

    # Add another sweep parameter to builder
    builder.add_sweep_definition(EMODTask.set_parameter_partial("Base_Infectivity"), [0.6, 1.0, 1.5, 2.0])

    # Add builder to templated simulations
    ts.add_builder(builder)

You can run a parameter sweep using the above code excerpt by running the included example, :py:class:`emodpy.examples.create_sims_eradication_from_github_url`.