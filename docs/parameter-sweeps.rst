====================================
Parameter sweeps and model iteration
====================================

In modeling, parameter sweeps are an important method for fine-tuning parameter values, exploring
parameter space, and calibrating simulations to data. A parameter sweep is an iterative process
in which simulations are run repeatedly using different values of the parameter(s) of choice. This
process enables the modeler to determine a parameter's "best" value (or range of values), or
even where in parameter space the model produces desirable (or non-desirable) behaviors.

When fitting models to data, it is likely that there will be numerous parameters that do not have a
pre-determined value.  Some parameters will have a range of values that are biologically plausible,
or have been determined from previous experiments; however, selecting a particular numerical value
to use in the model may not be feasible or realistic. Therefore, the best practice involves using a
parameter sweep to narrow down the  range of possible values or to provide a range of outcomes for
those possible values.

|IT_s| provides an automated approach to parameter sweeps. With few lines of code, it is possible to
test the model over any range of parameter values, with any combination of parameters. 

.. Note that parameter sweeps are a simple method of model calibration, and there are more complex calibration algorithms available of |IT_s|.  See :doc:`calibrate` for more information on additional methods.

.. contents:: Contents
   :local:

.. Parameter sweeps for model calibration
.. ======================================

.. For more information on model calibration, see :doc:`calibrate`.

.. Parameter sweeps and stochasticity
.. ==================================

.. this is the "iteration" bit
.. this should not be EMOD specific

With a stochastic model (such as |EMOD_s|), it is especially important to utilize parameter sweeps,
not only for calibration to data or parameter selection, but to fully explore the stochasticity in
output. Single model runs may appear to provide good fits to data, but variation will arise and
multiple runs are necessary to determine the appropriate range of parameter values necessary to
achieve  desired outcomes. Multiple iterations of a single set of parameter values should be run to
determine trends in simulation output: a single simulation output could provide results that are due
to random chance.

How to do parameter sweeps
==========================

With idmtools, you can do parameter sweeps with builders or without builders using a base task to set
your simulation parameters.

The typical 'output' of |IT_s| is a config.json file for each created simulation, which contains
the parameter values assigned: both the constant values and those being swept.

Using builders
--------------
In this release, to support parameter sweeps for models, we have the following builders to assist you:
    #. :py:class:`~idmtools.builders.simulation_builder.SimulationBuilder` - you set your sweep parameters in your scripts and it generates a config.json file with your sweeps for your experiment/simulations to use
    #. :py:class:`~idmtools.builders.csv_simulation_builder.CSVExperimentBuilder` - you can use a CSV file to do your parameter sweeps
    #. :py:class:`~idmtools.builders.yaml_simulation_builder.YamlSimulationBuilder` - you can use a Yaml file to do your parameter sweeps
    #. :py:class:`~idmtools.builders.arm_simulation_builder.ArmSimulationBuilder` for cross and pair parameters, which allows you to cross parameters, like you cross your arms.

There are two types of sweeping, cross and pair. Cross means you have for example, 3 x 3 = 9 set of parameters, and pair means 3 + 3 = 3 pairs of parameters, for example, a, b, c and d, e, f.

For cross sweeping, let's say again you have parameters a, b, c and d, e, f that you want to cross so you would have the following possible matches:
- a & d
- a & e
- a & f
- b & d
- b & e
- b & f
- c & d
- c & e
- c & f

For Python models, we also support them using a JSONConfiguredPythonTask. In the future we will support additional configured tasks for Python and R models.

Add sweep definition
^^^^^^^^^^^^^^^^^^^^

You can use the following two different methods for adding a sweep definition to a builder object:

- add_sweep_definition
- add_multiple_parameter_sweep_definition

Generally add_sweep_definition is used; however, in scenarios where you need to add multiple parameters to the sweep definition you use add_multiple_parameter_sweep_definiton - as seen in `idmtools.examples.python_model.multiple_parameter_sweeping.py`. More specifically, 
add_multiple_parameter_sweep_definition is used for sweeping with the same definition callback that takes multiple parameters, where 
the parameters can be a list of arguments or a list of keyword arguments. The sweep function will do cross-product sweeps between 
the parameters.

Creating sweeps without builders
--------------------------------
You can also create sweeps without using builders. Like this example:

.. code-block:: python

        """
                This file demonstrates how to create param sweeps without builders.

                we create base task including our common assets, e.g. our python model to run
                we create 5 simulations and for each simulation, we set parameter 'a' = [0,4] and 'b' = a + 10 using this task
                then we are adding this to task to our Experiment to run our simulations
        """
        import copy
        import os
        import sys

        from idmtools.assets import AssetCollection
        from idmtools.core.platform_factory import Platform
        from idmtools.entities.experiment import Experiment
        from idmtools.entities.simulation import Simulation
        from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
        from idmtools_test import COMMON_INPUT_PATH

        if __name__ == "__main__":

            # define our platform
            platform = Platform('COMPS2')

            # create experiment  object and define some extra assets
            assets_path = os.path.join(COMMON_INPUT_PATH, "python", "Assets")
            e = Experiment(name=os.path.split(sys.argv[0])[1],
                           tags={"string_tag": "test", "number_tag": 123},
                           assets=AssetCollection.from_directory(assets_path))

            # define paths to model and extra assets folder container more common assets
            model_path = os.path.join(COMMON_INPUT_PATH, "python", "model.py")

            # define our base task including the common assets. We could also add these assets to the experiment above
            base_task = JSONConfiguredPythonTask(script_path=model_path, envelope='parameters')
            base_simulation = Simulation.from_task(base_task)

            # now build our simulations
            for i in range(5):
                # first copy the simulation
                sim = copy.deepcopy(base_simulation)
                # configure it
                sim.task.set_parameter("a", i)
                sim.task.set_parameter("b", i + 10)
                # and add it to the simulations
                e.simulations.append(sim)

            # run the experiment
            e.run(platform=platform)
            # wait on it
            # in most real scenarios, you probably do not want to wait as this will wait until all simulations
            # associated with an experiment are done. We do it in our examples to show feature and to enable
            # testing of the scripts
            e.wait()
            # use system status as the exit code
            sys.exit(0 if e.succeeded else -1)


Running parameter sweeps in specific models
-------------------------------------------

The following pages provide information about running parameter sweeps in particular models, and
include example scripts.

.. want to add in model-specific sub-pages

.. toctree::
   :maxdepth: 3
   :titlesonly:
   :caption: Model-specific parameter sweep information

   sweeps-r
   sweeps-python
   sweeps-emod