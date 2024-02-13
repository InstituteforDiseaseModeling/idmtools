"""
idmtools SimulationBuilder definition.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import copy
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
        .. literalinclude:: ../../examples/builders/simulation_builder.py

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

    def add_sweep_definition(self, function: TSweepFunction, *args, **kwargs):
        self.add_multiple_parameter_sweep_definition(function, *args, **kwargs)

    @staticmethod
    def _map_argument_array(parameters, value, param) -> Dict[str, Iterable]:
        """
        Map multi-argument calls to parameters in a callback.
        Args:
            parameters: Parameters
            value_set: List of values that should be sent to parameter in calls

        Returns:
            Dictionary to map our call to our callbacks
        """
        call_args = copy.deepcopy(parameters)
        call_args[param] = value
        return call_args

    def _extract_remaining_parameters(self, function):
        # Retrieve all the parameters in the signature of the function
        parameters = signature(function).parameters
        # Ensure `simulation` is part of the parameter list
        if self.SIMULATION_ATTR not in parameters:
            raise ValueError(f"The function {function} passed to SweepBuilder.add_sweep_definition "
                             f"needs to take a {self.SIMULATION_ATTR} argument!")
        # Retrieve all the free parameters of the signature (other than `simulation`)
        remaining_parameters = {name: param.default for name, param in parameters.items() if
                                name != self.SIMULATION_ATTR and not isinstance(param.default, pd.DataFrame)}
        return remaining_parameters

    def case_args_tuple(self, function: TSweepFunction, remaining_parameters, values):
        # this is len(values) > 0 case
        required_params = {k: v for k, v in remaining_parameters.items() if v == inspect.Parameter.empty}
        _values = [self._validate_item(vals) for vals in values]

        if len(required_params) != len(values):
            if len(values) != 1 or len(required_params) > 0 or len(remaining_parameters) != 1:
                raise ValueError(
                    f"Currently the callback has {len(required_params)} required parameters and there were {len(values)} arguments passed.")
            else:
                # Special case: len(values) == 1 and len(required_params) == 0 (all have default values)
                # We assume the values is the input for the fist parameter
                param = list(remaining_parameters)[0]
                self.sweeps.append(
                    partial(function, **self._map_argument_array(remaining_parameters, v, param)) for v in _values[0])
                list(map(self._update_count, _values))
        else:
            # Now we have len(_values) == len(valid_params)

            # create sweeps using the multi-index
            generated_values = product(*_values)

            self.sweeps.append(
                partial(function, **self._map_multi_argument_array(list(required_params), v)) for v in
                generated_values)
            list(map(self._update_count, _values))

    def case_kwargs(self, function: TSweepFunction, remaining_parameters, values):
        required_params = {k: v for k, v in remaining_parameters.items() if v == inspect.Parameter.empty}

        extra_inputs = list(set(values) - set(remaining_parameters))
        if len(extra_inputs) > 0:
            raise ValueError(
                f"Extra arguments passed: {extra_inputs if len(extra_inputs) > 1 else extra_inputs[0]}.")

        missing_params = list(set(required_params) - set(values))
        if len(missing_params) > 0:
            raise ValueError(
                f"Missing arguments: {missing_params if len(missing_params) > 1 else missing_params[0]}.")

        # validate each values in a dict
        _values = {key: self._validate_item(vals) for key, vals in values.items()}
        generated_values = product(*_values.values())
        self.sweeps.append(
            partial(function, **self._map_multi_argument_array(_values.keys(), v)) for v in generated_values)
        list(map(self._update_count, _values.values()))

    def add_multiple_parameter_sweep_definition(self, function: TSweepFunction, *args, **kwargs):
        """
        Add a sweep definition callback that takes multiple parameters.

        The sweep will be defined as a cross-product between the parameters passed.

        Args:
            function: The sweep function, which must include a **simulation** parameter (or
                whatever is specified in :attr:`~idmtools.builders.ExperimentBuilder.SIMULATION_ATTR`).
            args: List of arguments to be passed
            kwargs: List of keyword arguments to be passed

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
            raise ValueError(
                "Currently in multi-argument sweep definitions, you have to supply either a arguments or keyword arguments, but not both.")
        if len(args) > 0:
            # args is always a tuple
            values = args
            # Consider special case: make it easy to use
            if len(values) == 1 and isinstance(values[0], dict):
                values = values[0]
                self.case_kwargs(function, remaining_parameters, values)
            else:
                self.case_args_tuple(function, remaining_parameters, values)
        elif len(kwargs) > 0:
            values = kwargs
            self.case_kwargs(function, remaining_parameters, values)
        else:
            required_params = {k: v for k, v in remaining_parameters.items() if v == inspect.Parameter.empty}
            if len(required_params) > 0:
                raise ValueError(f"Missing arguments: {list(required_params)}.")
            self.sweeps.append((function,))
            self._update_count([])

    def _validate_item(self, item):
        """
        Validate inputs.
        Args:
            item: input
        Returns:
            validated item
        """
        if isinstance(item, str):
            return [item]
        elif not isinstance(item, Iterable):
            return [item]
        elif hasattr(item, '__len__'):
            if isinstance(item, dict):
                # return [item]
                return item
            else:
                return item
            return item
        else:
            return list(item)

    @staticmethod
    def _map_multi_argument_array(parameters, value_set, remainder: str = None) -> Dict[str, Iterable]:
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

        if remainder:
            return {remainder: call_args}
        else:
            return call_args

    def _update_count(self, values):
        """
        Update count of sweeps.
        Args:
            values :Values to count

        Returns:
            None
        """
        if self.count == 0:
            if len(values) == 0:
                self.count = 1
            else:
                self.count = len(values)
        else:
            self.count *= len(values)

    def __iter__(self):
        """
        Iterator of the simulation builder.
        We duplicate the generators here so that we can loop over multiple times.
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
