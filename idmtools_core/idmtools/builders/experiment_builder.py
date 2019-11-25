import inspect
import typing
from functools import partial
from inspect import signature
from itertools import product

if typing.TYPE_CHECKING:
    from typing import Callable, Any, List, Iterable, Union


class ExperimentBuilder:
    """
    Class that represents an experiment builder.
    """
    # The keyword searched in the function used for sweeps
    SIMULATION_ATTR = 'simulation'

    def __init__(self):
        self.sweeps = []
        self.count = 1

    def add_sweep_definition(self, function: 'Callable', values: 'Union[List[Any], Iterable]'):
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
        remaining_parameters = [name for name, param in parameters.items() if
                                name != self.SIMULATION_ATTR and param.default == inspect.Parameter.empty]

        # If we have more than one free parameter => error
        if len(remaining_parameters) > 1:
            raise ValueError(f"The function {function} passed to SweepBuilder.add_sweep_definition "
                             f"needs to only have {self.SIMULATION_ATTR} and exactly one free parameter.")

        # Specially handle string case
        if isinstance(values, str):
            values = [values]

        # Everything is OK, create a partial to have everything set in the signature except `simulation` and add
        self.sweeps.append((partial(function, **{remaining_parameters[0]: v})) for v in values)

        self.count *= len(values)

    def __iter__(self):
        yield from product(*self.sweeps)
