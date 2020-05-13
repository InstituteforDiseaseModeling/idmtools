======================
Create simulation tags
======================

During the creation of simulations you can add tags, key:value pairs, included as metadata. The tags can be used for filtering on and searching for simulations. |IT_s| includes multiple ways for adding tags to simulations:

* (Preferred) Builder callbacks with :py:class:`~idmtools.builders.simulation_builder.SimulationBuilder` or :py:class:`~idmtools.entities.simulation.Simulation`
* Base task with :py:class:`~idmtools.entities.templated_simulation.TemplatedSimulations`
* Convert simulation from :py:class:`~idmtools.entities.templated_simulation.TemplatedSimulations` to a list

(Preferred) Builder callbacks
=============================
You can add tags to simulations by using builder callbacks while building experiments with **SimulationBuilder** or **Simulation** classes. This way supports adding tags to a large set of simulations and gives you full control over the simulation/task object. In addition, built-in tag management support is used when implementing the return values in a dictionary for the tags. The following example shows how to do this using **SimulationBuilder**::

    def update_sim(sim, parameter, value):
        sim.task.set_parameter(parameter, value)
        # set sim tasks,
        return {'custom': 123, parameter:value)
    builder = SimulationBuilder()
    set_run_number = partial(update_sim, param="Run_Number")
    builder.add_sweep_definition(set_run_number, range(0, 2))
    # create experiment from builder
    exp = Experiment.from_builder(builder, task, name=expname)

Base task with TemplatedSimulations
===================================
You can add tags to the base task used with the 
**TemplatedSimulations** class while building simulations, as shown in the following example::
    
    ts = TemplatedSimulations(base_task=task)
    ts.tags = {'a': 'test', 'b': 9}
    ts.add_builder(builder)

Convert simulation from TemplatedSimulations
============================================
If you need to add a tag to a specific simulation after building simulations from task with **TemplatedSimulations**, then you must convert the simulations to a list - as shown in the following example::

    experiment =  Experiment.from_builder(builder, task, name=expname)
    experiment.simulations = list(experiment.simulations)
    experiment.simulations[2].tags['test']=123

