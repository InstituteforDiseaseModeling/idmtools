"""
idmtools SimulationBuilder definition.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import inspect
from functools import partial
from inspect import signature
from itertools import product
from typing import Callable, Any, List, Iterable, Union, Dict
from idmtools.entities.simulation import Simulation
from idmtools.utils.collections import duplicate_list_of_generators

TSweepFunction = Union[
    Callable[[Simulation, Any], Dict[str, Any]],
    partial
]


class SimulationBuilder:
    """
    Class that represents an experiment builder.

    Examples:
        .. literalinclude:: ../examples/builders/simulation_builder.py

        Add tags with builder callbacks::

            def update_sim(sim, parameter, value):
                sim.task.set_parameter(parameter, value)
                # set sim tasks,
                return {'custom': 123, parameter:value)

            builder = SimulationBuilder()
            set_run_number = partial(update_sim, param="Run_Number")
            builder.add_sweep_definition(set_run_number, range(0, 2))
            # create experiment from builder
            exp = Experiment.from_builder(builder, task, name=expname)
    """
    # The keyword searched in the function used for sweeps
    SIMULATION_ATTR = 'simulation'

    def __init__(self):
        """
        Constructor.
        """
        self.sweeps = []
        self.count = 0

    def add_sweep_definition(self, function: TSweepFunction,
                             values: Union[List[Any], Iterable]):
        """
        Add a parameter sweep definition.

        A sweep definition is composed of a function and a list of values to call the function with.

        Args:
            function: The sweep function, which must include a **simulation** parameter (or
                whatever is specified in :attr:`~idmtools.builders.ExperimentBuilder.SIMULATION_ATTR`).
                The function also must include EXACTLY ONE free parameter, which the values will be passed to.
                The function can also be a partial--any Callable type will work.
            values: The list of values to call the function with.

        Examples:
            Examples of valid function::

                def myFunction(simulation, parameter):
                    pass

            How to deal with functions requiring more than one parameter?
            Consider the following function::

                python
                def myFunction(simulation, a, b):
                    pass

            Partial solution::

                python
                from functools import partial
                func = partial(myFunction, a=3)
                eb.add_sweep_definition(func, [1,2,3])

            Callable class solution::

                class setP:
                    def __init__(self, a):
                        self.a = a

                    def __call__(self, simulation, b):
                        return param_update(simulation, self.a, b)

                eb.add_sweep_definition(setP(3), [1,2,3])
        """
        # Retrieve all the parameters in the signature of the function
        parameters = signature(function).parameters

        # Ensure `simulation` is part of the parameter list
        if self.SIMULATION_ATTR not in parameters:
            raise ValueError(f"The function {function} passed to SweepBuilder.add_sweep_definition "
                             f"needs to take a {self.SIMULATION_ATTR} argument!")

        # Retrieve all the free parameters of the signature (other than `simulation`)
        remaining_parameters = [name for name, param in parameters.items() if name != self.SIMULATION_ATTR and param.default == inspect.Parameter.empty]

        # If we have more than one free parameter => error
        if len(remaining_parameters) > 1:
            raise ValueError(f"The function {function} passed to SweepBuilder.add_sweep_definition "
                             f"needs to only have {self.SIMULATION_ATTR} and exactly one free parameter.")

        # Specially handle string case
        if isinstance(values, str):
            values = [values]

        # Everything is OK, create a partial to have everything set in the signature except `simulation` and add
        self.sweeps.append((partial(function, **{remaining_parameters[0]: v})) for v in values)

        if self.count > 0:
            self.count *= len(values)
        else:
            self.count = len(values)

    def __iter__(self):
        """
        Iterator of the simulation builder.

        We duplicate the generators here so we can loop over multiple times.

        Returns:
            The iterator
        """
        old_sw, new_sw = duplicate_list_of_generators(self.sweeps)

        yield from product(*old_sw)
        self.sweeps = new_sw

    def __len__(self):
        """
        Total simulations to be built by builder. This is a Product of all total values for each sweep.

        Returns:
            Simulation count
        """
        return self.count
