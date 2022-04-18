"""
idmtools SimulationBuilder definition.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import pandas as pd
import inspect
from functools import partial
from inspect import signature
from itertools import product
from typing import Callable, Any, Iterable, Union, Dict
from idmtools.entities.simulation import Simulation
from idmtools.utils.collections import duplicate_list_of_generators

TSweepFunction = Union[
    Callable[[Simulation, Any], Dict[str, Any]],
    partial
]

MULTIPLE_ARGS_MUST_BE_ITERABLE_ERROR = "When defining a sweep across multiple parameters, they must be specified either in a Dict in the form of {{ KeyWork: Values }} where values is a list or [ Param1-Vals, Param2-Vals] where Param1-Vals and Param2-Vals are lists/iterables."
PARAMETER_LENGTH_MUST_MATCH_ERROR = "The parameters in the callback must match the length of the arguments/keyword arguments passed."


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

    def add_sweep_definition(self, function: TSweepFunction, values):
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
        remaining_parameters = self._extract_remaining_parameters(function)

        # If we have more than one free parameter => error
        if len(remaining_parameters) > 1:
            raise ValueError(f"The function {function} passed to SweepBuilder.add_sweep_definition "
                             f"needs to only have {self.SIMULATION_ATTR} and exactly one free parameter.")

        # Specially handle string case
        if isinstance(values, str):
            values = [values]

        # Everything is OK, create a partial to have everything set in the signature except `simulation` and add
        self.sweeps.append((partial(function, **{remaining_parameters[0]: v})) for v in values)
        self._update_count(values)

    def _extract_remaining_parameters(self, function):
        # Retrieve all the parameters in the signature of the function
        parameters = signature(function).parameters
        # Ensure `simulation` is part of the parameter list
        if self.SIMULATION_ATTR not in parameters:
            raise ValueError(f"The function {function} passed to SweepBuilder.add_sweep_definition "
                             f"needs to take a {self.SIMULATION_ATTR} argument!")
        # Retrieve all the free parameters of the signature (other than `simulation`)
        remaining_parameters = [name for name, param in parameters.items() if name != self.SIMULATION_ATTR and not isinstance(param.default, pd.DataFrame) and param.default == inspect.Parameter.empty]
        return remaining_parameters

    def add_multiple_parameter_sweep_definition(self, function: TSweepFunction, *args, **kwargs):
        """
        Add a sweep definition callback that takes multiple parameters.

        The sweep will be defined as a cross-product between the parameters passed.


        Args:
            function: The sweep function, which must include a **simulation** parameter (or
                whatever is specified in :attr:`~idmtools.builders.ExperimentBuilder.SIMULATION_ATTR`).
            *args: List of arguments to be passed
            **kwargs: List of keyword arguments to be passed

        Returns:
            None. Updates the Sweeps

        Examples:

            Examples of valid functions::

                # This function takes two parameters
                def myFunction(simulation, parameter_a, parameter_b):
                    pass

                # Function that takes three parameters
                def three_param_callback(simulation, parameter_a, parameter_b, parameter_c):
                    pass

            Calling Sweeps that take multiple parameters::

                # This example references the above valid function example
                sb = SimulationBuilder()

                # Add a sweep on the myFunction that takes two parameters.
                # Here we sweep the values 1-4 on parameter_a and a,b on parameter_b
                sb.add_multiple_parameter_sweep_definition(myFunction, range(1,5), ["a", "b"])

                sb2 = SimulationBuilder()
                # Example calling using a dictionary instead
                sb.add_multiple_parameter_sweep_definition(three_param_callback, dict(parameter_a=range(1,5), parameter_b=["a", "b"], parameter_c=range(4,5))
                # The following is equivalent
                sb.add_multiple_parameter_sweep_definition(three_param_callback, **dict(parameter_a=range(1,5), parameter_b=["a", "b"], parameter_c=range(4,5))

        """
        remaining_parameters = self._extract_remaining_parameters(function)
        if len(args) > 0 and len(kwargs) > 0:
            raise ValueError("Currently in multi-argument sweep definitions, you have to supply either a arguments or keyword arguments, but not both.")
        if len(args) > 0:
            values = args
            if isinstance(values, (list, tuple)) and len(values) == 1 and isinstance(values[0], dict):
                values = values[0]
        elif len(kwargs) > 0:
            values = kwargs
        else:
            raise ValueError("This method expects either a list of lists or a dictionary that defines the sweeps")

        if len(remaining_parameters) <= 1:
            raise ValueError("This method expects either a list of lists or a dictionary that defines the sweeps. In addition, currently we do not support over-riding default values for parameters")

        if isinstance(values, (list, tuple)):
            if len(values) == len(remaining_parameters):
                # validate each values is a list
                for idx, value in enumerate(values):
                    if not isinstance(value, Iterable):
                        raise ValueError(f"{MULTIPLE_ARGS_MUST_BE_ITERABLE_ERROR} Please correct item at index {value}")

                # create sweeps using the multi-index
                list(map(self._update_count, values))
                generated_values = product(*values)
                self.sweeps.append(partial(function, **self._map_multi_argument_array(remaining_parameters, v)) for v in generated_values)
            else:
                raise ValueError(f"{PARAMETER_LENGTH_MUST_MATCH_ERROR} Currently the callback has {len(remaining_parameters)} parameters and there were {len(values)} arguments passed.")
        elif isinstance(values, dict):
            if len(values.keys()) != len(remaining_parameters):
                raise ValueError(f"{PARAMETER_LENGTH_MUST_MATCH_ERROR}. Currently the callback has {len(remaining_parameters)} parameters and there were {len(values.keys())} arguments passed.")
            for key, vals in values.items():
                if not isinstance(vals, Iterable):
                    raise ValueError(f"{MULTIPLE_ARGS_MUST_BE_ITERABLE_ERROR} Please correct item at index {key}")
                elif key not in remaining_parameters:
                    raise ValueError(f"Unknown keyword parameter passed: {key}. Support keyword args are {', '.join(remaining_parameters)}")
            list(map(self._update_count, values))
            generated_values = product(*values.values())
            self.sweeps.append(partial(function, **self._map_multi_argument_array(values.keys(), v)) for v in generated_values)

    @staticmethod
    def _map_multi_argument_array(parameters, value_set) -> Dict[str, Iterable]:
        """
        Map multi-argument calls to parameters in a callback.

        Args:
            parameters: Parameters
            value_set: List of values that should be sent to parameter in calls

        Returns:
            Dictionary to map our call to our callbacks
        """
        call_args = dict()
        for idx, parameter in enumerate(parameters):
            call_args[parameter] = value_set[idx]
        return call_args

    def _update_count(self, values):
        """
        Update count of sweeps.

        Args:
            values :Values to count

        Returns:
            None
        """
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
