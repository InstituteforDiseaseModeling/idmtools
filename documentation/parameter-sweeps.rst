====================================
Parameter sweeps and model iteration
====================================


In modeling, parameter sweeps are an important method for fine-tuning parameter values, exploring
parameter space, and calibrating simulations to data. A parameter sweep is an iterative process
in which simulations are run repeatedly using different values of the parameter(s) of choice. This
process enables the modeler to determine what a parameter's "best" value (or range of values), or
even where in parameter space the model produces desirable (or non-desirable) behaviors.

When fitting models to data, it is likely that there will be numerous parameters that do not have a
pre-determined value.  Some parameters will have a range of values that are biologically plausible,
or have been determined from previous experiments; however, selecting a particular numerical value
to use in the model may not be feasible or realistic. Therefore, the best practice involves using a
parameter sweep to narrow down the  range of possible values or to provide a range of outcomes for
those possible values.

|DT| provides an automated approach to parameter sweeps. With few lines of code, it is possible to
test the model over any range of parameter values, with any combination of parameters. Note that
parameter sweeps may also be used for model calibration. See :doc:`calibrate` for more information.



.. contents:: Contents
   :local:


Parameter sweeps and stochasticity
==================================

.. this is the "iteration" bit

With a stochastic model such as |EMOD_s|, it is especially important to utilize parameter sweeps.
Multiple iterations of a single set of parameter values should be run to determine trends in
simulation output: a single simulation output could provide results that are due to random chance.

In |EMOD_s|, the parameter **Run_Number** determines the seed for the random number generator.
If **Run_Number** is not changed, each simulation will result in the same output. Therefore,
to explore the stochastic nature of the model, a parameter sweep of **Run_Number** must be
conducted. This will run the simulation with different random number seeds, so ...



Examples
========

.. names below are just placeholders for the various examples that exist in the example > sweeps folder

general
-------


drug_campaign
-------------


drug_vector_param_sweep
-----------------------


larvicides
----------


.. this is ported over from dtk-tools. will need to be updated/fixed/etc....these examples may not even exist anymore