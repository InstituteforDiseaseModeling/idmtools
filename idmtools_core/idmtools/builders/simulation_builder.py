"""
idmtools SimulationBuilder definition.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import inspect
import numpy as np
import pandas as pd
from functools import partial
from inspect import signature
from itertools import product
from typing import Callable, Any, Iterable, Union, Dict, Sized
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
        self.__count = 0

    @property
    def count(self):
        return self.__count

    @count.setter
    def count(self, cnt):
        """
        Set the count property.
        Args:
            cnt: count set
        Returns:
            int
        """
        if self.__count == 0:
            self.__count = cnt
        else:
            self.__count = self.__count * cnt

    def add_sweep_definition(self, function: TSweepFunction, *args, **kwargs):
        """
        Add a sweep definition callback that takes possible multiple parameters (None or many).

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

                # This function takes one parameter
                def myFunction(simulation, parameter_a):
                    pass

               # This function takes one parameter with default value
                def myFunction(simulation, parameter_a=6):
                    pass

                # This function takes two parameters (parameters may have default values)
                def myFunction(simulation, parameter_a, parameter_b=9):
                    pass

                # Function that takes three parameters (parameters may have default values)
                def three_param_callback(simulation, parameter_a, parameter_b, parameter_c=10):
                    pass

            Calling Sweeps that take multiple parameters::

                # This example references the above valid function example
                sb = SimulationBuilder()

                # Add a sweep on the myFunction that takes parameter(s).
                # Here we sweep the values 1-4 on parameter_a and a,b on parameter_b
                sb.add_sweep_definition(myFunction, range(1,5), ["a", "b"])

                sb2 = SimulationBuilder()
                # Example calling using a dictionary instead
                sb.add_sweep_definition(three_param_callback, dict(parameter_a=range(1,5), parameter_b=["a", "b"], parameter_c=range(4,5))
                # The following is equivalent
                sb.add_sweep_definition(three_param_callback, **dict(parameter_a=range(1,5), parameter_b=["a", "b"], parameter_c=range(4,5))

                sb3 = SimulationBuilder()
                # If all parameters have default values, we can even simply do
                sb3.add_sweep_definition(three_param_callback)

            Remark: in general::

                def my_callback(simulation, parameter_1, parameter_2, ..., parameter_n):
                    pass

            Calling Sweeps that take multiple parameters::

                sb = SimulationBuilder()
                sb.add_sweep_definition(my_callback, Iterable_1, Iterable_2, ..., Iterable_m)

                # Note: the # of Iterable object must match the parameters # of my_callback, which don't have default values

                # Or use the key (parameter names)

                sb = SimulationBuilder()
                sb.add_sweep_definition(my_callback, parameter_1=Iterable_1, parameter_2=Iterable_2, ..., parameter_m=Iterable_m)
                # The following is equivalent
                sb.add_sweep_definition(my_callback, dict(parameter_1=Iterable_1, parameter_2=Iterable_2, ..., parameter_m=Iterable_m))
                # and
                sb.add_sweep_definition(my_callback, **dict(parameter_1=Iterable_1, parameter_2=Iterable_2, ..., parameter_m=Iterable_m))
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
            required_params = self._extract_required_parameters(remaining_parameters)
            if len(required_params) > 0:
                raise ValueError(f"Missing arguments: {list(required_params)}.")
            self.sweeps.append((function,))
            self.count = 1

    def _extract_remaining_parameters(self, function):
        # Retrieve all the parameters in the signature of the function
        parameters = signature(function).parameters
        # Ensure `simulation` is part of the parameter list
        if self.SIMULATION_ATTR not in parameters:
            raise ValueError(f"The callback function passed to SweepBuilder.add_sweep_definition "
                             f"needs to take a {self.SIMULATION_ATTR} argument!")
        # Retrieve all the free parameters of the signature (other than `simulation`)
        remaining_parameters = {name: param.default for name, param in parameters.items() if
                                name != self.SIMULATION_ATTR}
        return remaining_parameters

    def case_args_tuple(self, function: TSweepFunction, remaining_parameters, values):
        # this is len(values) > 0 case
        required_params = self._extract_required_parameters(remaining_parameters)
        _values = [self._validate_value(vals) for vals in values]

        if len(required_params) > 0 and len(required_params) != len(values):
            if len(remaining_parameters) != len(values):
                raise ValueError(
                    f"Currently the callback has {len(required_params)} required parameters and callback has {len(remaining_parameters)} parameters but there were {len(values)} arguments passed.")
            else:
                # Handle special case
                generated_values = product(*_values)
                self.sweeps.append(
                    partial(function, **self._map_argument_array(list(remaining_parameters), v)) for v in
                    generated_values)
                self.count = np.prod(list(map(len, _values)))
                return

        if len(required_params) == 0 and len(values) > 1:
            raise ValueError(
                f"Currently the callback {len(remaining_parameters)} parameters (all have default values) and there were {len(values)} arguments passed.")

        if len(required_params) == 0 and len(remaining_parameters) != 1:
            raise ValueError(
                f"Currently the callback has {len(remaining_parameters)} parameters (all have default values) and there were {len(values)} arguments passed.")

        # Now we come to two cases
        # 1. len(required_params) > 0 and len(required_params) == len(values)
        # 2. len(required_params) == 0 and len(remaining_parameters) == 1 and len(values) == 1
        # create sweeps using the multi-index
        generated_values = product(*_values)
        if len(required_params) > 0:
            self.sweeps.append(
                partial(function, **self._map_argument_array(list(required_params), v)) for v in
                generated_values)
        else:
            self.sweeps.append(
                partial(function, **self._map_argument_array(list(remaining_parameters), v)) for v in
                generated_values)

        self.count = np.prod(list(map(len, _values)))

    def case_kwargs(self, function: TSweepFunction, remaining_parameters, values):
        required_params = self._extract_required_parameters(remaining_parameters)
        extra_inputs = list(set(values) - set(remaining_parameters))
        if len(extra_inputs) > 0:
            raise ValueError(
                f"Extra arguments passed: {extra_inputs if len(extra_inputs) > 1 else extra_inputs[0]}.")

        missing_params = list(set(required_params) - set(values))
        if len(missing_params) > 0:
            raise ValueError(
                f"Missing arguments: {missing_params if len(missing_params) > 1 else missing_params[0]}.")

        # validate each values in a dict
        _values = {key: self._validate_value(vals) for key, vals in values.items()}
        generated_values = product(*_values.values())
        self.sweeps.append(
            partial(function, **self._map_argument_array(_values.keys(), v)) for v in generated_values)
        self.count = np.prod(list(map(len, _values.values())))

    def add_multiple_parameter_sweep_definition(self, function: TSweepFunction, *args, **kwargs):
        """
        Add a sweep definition callback that takes possible multiple parameters (None or many).

        The sweep will be defined as a cross-product between the parameters passed.

        Args:
            function: The sweep function, which must include a **simulation** parameter (or
                whatever is specified in :attr:`~idmtools.builders.ExperimentBuilder.SIMULATION_ATTR`).
            args: List of arguments to be passed
            kwargs: List of keyword arguments to be passed

        Returns:
            None. Updates the Sweeps

        Examples:
            Refer to the comments in the add_sweep_definition function for examples
        """
        self.add_sweep_definition(function, *args, **kwargs)

    def _validate_value(self, value):
        """
        Validate inputs.
        Args:
            value: input
        Returns:
            validated value
        """
        if isinstance(value, str):
            return [value]
        elif not isinstance(value, Iterable):
            return [value]
        # elif hasattr(value, '__len__'):
        elif isinstance(value, Sized):
            if isinstance(value, (dict, pd.DataFrame)):
                return [value]
            else:
                return value
        else:
            return list(value)

    @staticmethod
    def _map_argument_array(parameters, value_set, remainder: str = None) -> Dict[str, Iterable]:
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

    def _extract_required_parameters(self, remaining_parameters: Dict) -> Dict:
        required_params = {k: v for k, v in remaining_parameters.items() if
                           not isinstance(v, pd.DataFrame) and v == inspect.Parameter.empty}
        return required_params

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
