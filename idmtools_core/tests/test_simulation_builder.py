import allure
import itertools
from functools import partial

import pandas as pd
import pytest

from idmtools.builders import SimulationBuilder
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.json_configured_task import JSONConfiguredTask
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.test_task import TestTask

setA = partial(JSONConfiguredTask.set_parameter_sweep_callback, param="a")
setB = partial(JSONConfiguredTask.set_parameter_sweep_callback, param="b")


def update_parameter_callback(simulation, a, b, c):
    simulation.task.set_parameter("param_a", a)
    simulation.task.set_parameter("param_b", b)
    simulation.task.set_parameter("param_c", c)
    return {"a": a, "b": b, "c": c}


@pytest.mark.smoke
@allure.story("Sweeps")
@allure.suite("idmtools_core")
class TestSimulationBuilder(ITestWithPersistence):

    def setUp(self):
        super().setUp()
        self.builder = SimulationBuilder()

    def tearDown(self):
        super().tearDown()

    def get_templated_sim_builder(self):
        templated_sim = TemplatedSimulations(base_task=TestTask())
        templated_sim.builder = self.builder
        return templated_sim

    def get_simulations_with_builder(self, builder):
        templated_sim = TemplatedSimulations(base_task=TestTask())
        templated_sim.builder = builder
        simulations = list(templated_sim)
        return simulations

    def create_simple_sweep(self):
        self.builder.add_sweep_definition(setA, range(5))
        self.builder.add_sweep_definition(setB, [1, 2, 3])

    def test_simple_simulation_builder(self):
        self.create_simple_sweep()
        expected_values = list(itertools.product(range(5), [1, 2, 3]))
        templated_sim = self.get_templated_sim_builder()
        # convert template to a fully realized list
        simulations = list(templated_sim)

        # Test if we have correct number of simulations
        self.assertEqual(len(simulations), len(expected_values))
        # Verify simulations individually
        for simulation, value in zip(simulations, expected_values):
            expected_dict = {"a": value[0], "b": value[1]}
            self.assertEqual(simulation.task.parameters, expected_dict)

    def test_reverse_order(self):
        self.create_simple_sweep()

        templated_sim = self.get_templated_sim_builder()

        # convert template to a fully realized list
        simulations_cfgs = list([s.task.parameters for s in templated_sim])

        # reverse
        builder2 = SimulationBuilder()
        first = [1, 2, 3]
        second = range(5)
        builder2.add_sweep_definition(setB, first)
        builder2.add_sweep_definition(setA, second)
        self.assertEqual(builder2.count, len(first) * len(second))
        templated_sim2 = TemplatedSimulations(base_task=TestTask())
        templated_sim2.builder = builder2

        simulations2_cfgs = list([s.task.parameters for s in templated_sim2])

        for cfg in simulations_cfgs:
            self.assertIn(dict(b=cfg['b'], a=cfg['a']), simulations2_cfgs)

    # test add a single parameter sweep definition with one argument
    def test_add_single_parameter_sweep_definition_with_argument(self):
        builder = SimulationBuilder()

        def sweep_function(simulation, arg):
            assert isinstance(simulation, Simulation)
            simulation.task.set_parameter('param_a', arg)
            return {'arg': arg}

        test_args = [1, 2, 3]
        builder.add_sweep_definition(sweep_function, test_args)
        assert len(builder) == len(test_args)
        for i, sweep in enumerate(builder):
            assert sweep[0].keywords['arg'] == test_args[i]

        simulations = self.get_simulations_with_builder(builder)
        for i, simulation in enumerate(simulations):
            assert simulation.tags['arg'] == test_args[i]
            assert simulation.task.parameters == {'param_a': test_args[i]}

    # test add a single parameter sweep definition with arguments
    def test_add_single_parameter_sweep_definition_with_arguments(self):
        builder = SimulationBuilder()

        def sweep_function(simulation, arg1, arg2, arg3):
            simulation.task.set_parameter('arg1', arg1)
            simulation.task.set_parameter('arg2', arg2)
            simulation.task.set_parameter('arg3', arg3)
            return {'arg1': arg1, 'arg2': arg2, 'arg3': arg3}

        test_args = [1, 2, 3]
        builder.add_sweep_definition(sweep_function, *test_args)
        assert len(builder) == 1
        for i, sweep in enumerate(builder):
            assert sweep[0].keywords['arg1'] == test_args[0]
            assert sweep[0].keywords['arg2'] == test_args[1]
            assert sweep[0].keywords['arg3'] == test_args[2]

        simulations = self.get_simulations_with_builder(builder)
        for i, simulation in enumerate(simulations):
            assert simulation.tags['arg1'] == test_args[0]
            assert simulation.tags['arg2'] == test_args[1]
            assert simulation.tags['arg3'] == test_args[2]
            assert simulation.task.parameters == {'arg1': test_args[0], 'arg2': test_args[1], 'arg3': test_args[2]}

    # can handle a callback with a dictionary parameter as list
    def test_handle_callback_with_dictionary_parameter_as_list(self):
        builder = SimulationBuilder()

        def sweep_function(simulation, sweep_value):
            simulation.task.set_parameter('arg', sweep_value)
            return {'arg': sweep_value}

        test_args = [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]
        builder.add_sweep_definition(sweep_function, test_args)

        assert len(builder) == len(test_args) == 2

        for i, sweep in enumerate(builder):
            assert sweep[0].keywords['sweep_value'] == test_args[i]

        simulations = self.get_simulations_with_builder(builder)
        for i, simulation in enumerate(simulations):
            assert simulation.tags['arg'] == test_args[i]
            assert simulation.task.parameters == {'arg': test_args[i]}

    # can handle a callback with a dictionary parameters
    def test_add_single_parameter_sweep_definition_with_dict_arguments(self):
        builder = SimulationBuilder()

        def sweep_function(simulation, a, b, c):
            simulation.task.set_parameter('a', a)
            simulation.task.set_parameter('b', b)
            simulation.task.set_parameter('c', c)
            return {'a': a, 'b': b, 'c': c}

        builder.add_sweep_definition(sweep_function, dict(a=[1, 2], b=['a', 'b'], c=range(4, 6)))
        assert len(builder) == 8
        assert builder.count == 8

        expected_values = list(itertools.product([1, 2], ['a', 'b'], range(4, 6)))
        expected_results = []
        expected_tags = []
        for expected_value in expected_values:
            expected_results.append({'a': expected_value[0], 'b': expected_value[1], 'c': expected_value[2]})
            expected_tags.append({'a': expected_value[0], 'b': expected_value[1], 'c': expected_value[2]})

        for i, sweep in enumerate(builder):
            assert sweep[0].keywords == expected_results[i]

        simulations = self.get_simulations_with_builder(builder)
        for i, simulation in enumerate(simulations):
            assert simulation.tags == expected_tags[i]
            assert simulation.task.parameters == expected_tags[i]

    # can handle a callback with a dictionary parameter with single item
    def test_add_single_parameter_sweep_definition_with_dict_argument(self):
        builder = SimulationBuilder()

        def sweep_function(simulation, a):
            simulation.task.set_parameter('arg', a)
            return {'arg': a}

        builder.add_sweep_definition(sweep_function, dict({"a": 1}))

        assert len(builder) == 1
        for i, sweep in enumerate(builder):
            assert sweep[0].keywords['a'] == 1

        simulations = self.get_simulations_with_builder(builder)
        for i, simulation in enumerate(simulations):
            assert simulation.tags['arg'] == 1
            assert simulation.task.parameters == {'arg': 1}

    # can handle a callback with a string parameter as list
    def test_handle_callback_with_string_parameter_list(self):
        builder = SimulationBuilder()

        def sweep_function(simulation, sweep):
            simulation.task.set_parameter('arg', sweep)
            return {'arg': sweep}

        test_args = ['abc', 'def', 'ghi']
        builder.add_sweep_definition(sweep_function, test_args)
        assert len(builder) == len(test_args)
        for i, sweep in enumerate(builder):
            assert sweep[0].keywords['sweep'] == test_args[i]

        simulations = self.get_simulations_with_builder(builder)
        for i, simulation in enumerate(simulations):
            assert simulation.tags['arg'] == test_args[i]
            assert simulation.task.parameters == {'arg': test_args[i]}

            # can handle a callback with a string parameter

    def test_handle_callback_with_string_parameter(self):
        builder = SimulationBuilder()

        def sweep_function(simulation, sweep):
            simulation.task.set_parameter('arg', sweep)
            return {'arg': sweep}

        test_args = "abc"
        builder.add_sweep_definition(sweep_function, test_args)
        assert len(builder) == 1
        for i, sweep in enumerate(builder):
            assert sweep[0].keywords['sweep'] == test_args

        simulations = self.get_simulations_with_builder(builder)
        assert simulations[0].tags['arg'] == test_args
        assert simulations[0].task.parameters == {'arg': test_args}

    # can add a single parameter sweep definition with keyword arguments
    def test_add_single_parameter_sweep_definition_with_keyword_arguments(self):
        builder = SimulationBuilder()

        def sweep_function(simulation, arg):
            simulation.task.set_parameter('arg', arg)
            return {'my_arg': arg}

        builder.add_sweep_definition(sweep_function, arg=[1, 2, 3])
        assert len(builder) == 3
        for i, sweep in enumerate(builder):
            assert sweep[0].keywords['arg'] == i + 1
        simulations = self.get_simulations_with_builder(builder)
        for i, simulation in enumerate(simulations):
            assert simulation.tags['my_arg'] == i + 1
            assert simulation.task.parameters == {'arg': i + 1}

    # Adds a single parameter sweep definition with keyword arguments to the 'sweeps' list.
    def test_add_single_parameter_sweep_definition_with_keyword_arguments_1(self):
        builder = SimulationBuilder()

        def sweep_function(simulation, arg):
            simulation.task.set_parameter('arg', arg)
            return {'arg': arg}

        test_kwargs = {'arg': [1, 2, 3]}
        builder.add_sweep_definition(sweep_function, **test_kwargs)
        assert len(builder) == len(test_kwargs['arg'])
        for i, sweep in enumerate(builder):
            assert sweep[0].keywords['arg'] == test_kwargs['arg'][i]
        simulations = self.get_simulations_with_builder(builder)
        for i, simulation in enumerate(simulations):
            assert simulation.tags['arg'] == test_kwargs['arg'][i]
            assert simulation.task.parameters == {'arg': test_kwargs['arg'][i]}

    # Adds a single parameter sweep definition with mismatched keyword
    def test_add_single_parameter_sweep_definition_with_mismatch_keyword(self):
        builder = SimulationBuilder()

        def sweep_function(simulation, test_kwargs):
            simulation.task.set_parameter('arg', test_kwargs)
            return {'arg': test_kwargs}

        test_kwargs = {'arg': [1, 2, 3]}
        with pytest.raises(ValueError) as context:
            builder.add_sweep_definition(sweep_function, **test_kwargs)  # this is same as pass in arg=[1,2,3]
        assert context.value.args[0] == "Extra arguments passed: arg."

    # can handle a callback with a dictionary parameters
    def test_add_single_parameter_sweep_definition_with_dict_kwargs(self):
        builder = SimulationBuilder()

        def sweep_function(simulation, a, b, c):
            simulation.task.set_parameter('a', a)
            simulation.task.set_parameter('b', b)
            simulation.task.set_parameter('c', c)
            return {'a': a, 'b': b, 'c': c}

        builder.add_sweep_definition(sweep_function, **dict(a=[1, 2], b=['a', 'b'], c=range(4, 6)))

        assert len(builder) == builder.count == 8
        expected_values = list(itertools.product([1, 2], ['a', 'b'], range(4, 6)))
        expected_results = []
        expected_tags = []
        for expected_value in expected_values:
            expected_results.append({'a': expected_value[0], 'b': expected_value[1], 'c': expected_value[2]})
            expected_tags.append({'a': expected_value[0], 'b': expected_value[1], 'c': expected_value[2]})

        for i, sweep in enumerate(builder):
            assert sweep[0].keywords == expected_results[i]

        simulations = self.get_simulations_with_builder(builder)
        for i, simulation in enumerate(simulations):
            assert simulation.tags == expected_tags[i]
            assert simulation.task.parameters == expected_tags[i]

    # can add a single parameter sweep definition with single kwarg
    def test_add_single_parameter_sweep_definition_with_keyword_argument(self):
        builder = SimulationBuilder()

        def sweep_function(simulation, arg):
            simulation.task.set_parameter('arg', arg)
            return {'my_arg': arg}

        builder.add_sweep_definition(sweep_function, arg='test')
        assert len(builder) == 1
        assert builder.count == 1
        for i, sweep in enumerate(builder):
            assert sweep[0].keywords['arg'] == 'test'
        simulations = self.get_simulations_with_builder(builder)
        for i, simulation in enumerate(simulations):
            assert simulation.tags['my_arg'] == 'test'
            assert simulation.task.parameters == {'arg': 'test'}

    # test raises a ValueError when adding a single-argument sweep definition with too many arguments
    def test_raises_value_error_with_too_many_arguments(self):
        builder = SimulationBuilder()
        test_args = [1, 2, 3]
        with pytest.raises(ValueError) as context:
            def sweep_function(simulation, arg):
                return {'arg': arg}

            builder.add_sweep_definition(sweep_function, *test_args)  # *test_args is same as pass in 1,2,3 not [1,2,3]
        assert context.value.args[
                   0] == 'Currently the callback has 1 required parameters and callback has 1 parameters but there were 3 arguments passed.'

    # test handle a callback with no parameters
    def test_handle_callback_with_no_parameters(self):
        builder = SimulationBuilder()

        def sweep_function(simulation):
            return {}

        builder.add_sweep_definition(sweep_function)
        assert len(builder) == 1
        simulations = self.get_simulations_with_builder(builder)
        assert len(simulations) == 1
        assert simulations[0].task.parameters == {}

    # can handle a callback with default parameters
    def test_handle_callback_with_default_parameters(self):
        builder = SimulationBuilder()

        def sweep_function(simulation, sweep=10):
            simulation.task.set_parameter('arg', sweep)
            return {'sweep': sweep}

        builder.add_sweep_definition(sweep_function)

        assert len(builder) == 1

        simulations = self.get_simulations_with_builder(builder)
        assert len(simulations) == 1
        assert simulations[0].tags['sweep'] == 10
        assert simulations[0].task.parameters == {'arg': 10}

    # can handle a callback with mix default parameter and non default parameter
    def test_handle_callback_with_default_parameters_1(self):
        builder = SimulationBuilder()

        def sweep_function(simulation, sweep1, sweep2=10):
            simulation.task.set_parameter('arg1', sweep1)
            simulation.task.set_parameter('arg2', sweep2)
            return {'sweep_a': sweep1, 'sweep_b': sweep2}

        builder.add_sweep_definition(sweep_function, range(3))

        assert len(builder) == 3
        for i, sweep in enumerate(builder):
            assert sweep[0].keywords['sweep1'] == i

        simulations = self.get_simulations_with_builder(builder)
        assert len(simulations) == 3
        for i, simulation in enumerate(simulations):
            assert simulation.tags['sweep_a'] == i
            assert simulation.tags['sweep_b'] == 10
            assert simulation.task.parameters == {'arg1': i, 'arg2': 10}

    # can handle a callback with mix default parameters
    def test_handle_callback_with_default_parameters_2(self):
        builder = SimulationBuilder()

        def sweep_function(simulation, sweep1, sweep2=10):
            simulation.task.set_parameter('arg1', sweep1)
            simulation.task.set_parameter('arg2', sweep2)
            return {'sweep_a': sweep1, 'sweep_b': sweep2}

        sweep1 = range(3)
        sweep2 = [4, 5]
        builder.add_sweep_definition(sweep_function, sweep1, sweep2)

        assert len(builder) == 6
        expected_values = list(itertools.product(sweep1, sweep2))
        expected_results = []
        expected_tags = []
        expected_sweeps = []
        for expected_value in expected_values:
            expected_results.append({'arg1': expected_value[0], 'arg2': expected_value[1]})
            expected_tags.append({'sweep_a': expected_value[0], 'sweep_b': expected_value[1]})
            expected_sweeps.append({'sweep1': expected_value[0], 'sweep2': expected_value[1]})
        for i, sweep in enumerate(builder):
            assert sweep[0].keywords == expected_sweeps[i]

        simulations = self.get_simulations_with_builder(builder)
        assert len(simulations) == 6
        for i, simulation in enumerate(simulations):
            assert simulation.tags == expected_tags[i]
            assert simulation.task.parameters == expected_results[i]

    # can handle a callback with extra default parameter
    def test_handle_callback_with_default_parameters_3(self):
        builder = SimulationBuilder()

        def sweep_function(simulation, sweep1, sweep2=10, sweep3=20):
            simulation.task.set_parameter('arg1', sweep1)
            simulation.task.set_parameter('arg2', sweep2)
            return {'sweep_a': sweep1, 'sweep_b': sweep2}

        with pytest.raises(ValueError) as context:
            builder.add_sweep_definition(sweep_function, range(3), [4, 5])
        assert context.value.args[
                   0] == "Currently the callback has 1 required parameters and callback has 3 parameters but there were 2 arguments passed."

    # raises a ValueError when adding a single-argument sweep definition with no simulation argument
    def test_raises_value_error_single_argument_no_simulation(self):
        builder = SimulationBuilder()

        def sweep_function(sweep):
            return {'arg': sweep}

        with pytest.raises(ValueError) as context:
            builder.add_sweep_definition(sweep_function, [1, 2, 3])
        assert context.value.args[
                   0] == "The callback function passed to SweepBuilder.add_sweep_definition needs to take a simulation argument!"

    def test_raises_value_error_with_extra_arguments_in_dict(self):
        def my_func(simulation, a):  # test dict key mismatch ('a' vs 'aa' here)
            return {"first": a}

        with pytest.raises(ValueError) as context:
            self.builder.add_sweep_definition(my_func, dict({"aa": 1}))
        assert context.value.args[0] == "Extra arguments passed: aa."

    def test_add_sweep_definition_with_tuple(self):
        a = (4, 5, 6)
        b = (1, 2, 3)
        self.builder.add_sweep_definition(setA, a)
        self.builder.add_sweep_definition(setB, b)
        expected_values = list(itertools.product(a, b))
        self.assertEqual(self.builder.count, len(expected_values))
        templated_sim = self.get_templated_sim_builder()
        simulations = list(templated_sim)
        # Test if we have correct number of simulations
        self.assertEqual(len(simulations), len(expected_values))
        # Verify simulations individually
        for simulation, value in zip(simulations, expected_values):
            expected_dict = {"a": value[0], "b": value[1]}
            self.assertEqual(simulation.task.parameters, expected_dict)

    # can iterate over all possible combinations of sweep definitions
    def test_iterate_over_all_possible_combinations(self):
        builder = SimulationBuilder()

        # Define sweep functions
        def sweep_function_1(simulation, arg):
            simulation.task.set_parameter('arg', arg)
            return {'arg': arg}

        def sweep_function_2(simulation, arg1, arg2):
            simulation.task.set_parameter('arg1', arg1)
            simulation.task.set_parameter('arg2', arg2)
            return {'arg1': arg1, 'arg2': arg2}

        def sweep_function_3(simulation, arg3, arg4, arg5):
            simulation.task.set_parameter('arg3', arg3)
            simulation.task.set_parameter('arg4', arg4)
            simulation.task.set_parameter('arg5', arg5)
            return {'arg3': arg3, 'arg4': arg4, 'arg5': arg5}

        # Add sweep definitions
        builder.add_sweep_definition(sweep_function_1, [1, 2, 3])
        builder.add_sweep_definition(sweep_function_2, [4, 5], [6, 7])
        builder.add_sweep_definition(sweep_function_3, [8, 9], [10, 11], [12, 13])

        # Check the number of combinations
        assert len(builder) == 96

        # Iterate over all combinations and check the results
        expected_values = list(itertools.product([1, 2, 3], list(itertools.product([4, 5], [6, 7])),
                                                 list(itertools.product([8, 9], [10, 11], [12, 13]))))
        expected_results = []
        expected_tags = []
        for expected_value in expected_values:
            expected_results.append(({'arg': expected_value[0]},
                                     {'arg1': expected_value[1][0], 'arg2': expected_value[1][1]},
                                     {'arg3': expected_value[2][0], 'arg4': expected_value[2][1],
                                      'arg5': expected_value[2][2]}))
            expected_tags.append({'arg': expected_value[0], 'arg1': expected_value[1][0], 'arg2': expected_value[1][1],
                                  'arg3': expected_value[2][0], 'arg4': expected_value[2][1],
                                  'arg5': expected_value[2][2]})

        for i, sweep in enumerate(builder):
            assert set(sweep[0].keywords) == set(expected_results[i][0])
            assert set(sweep[1].keywords) == set(expected_results[i][1])
            assert set(sweep[2].keywords) == set(expected_results[i][2])

        simulations = self.get_simulations_with_builder(builder)
        for i, simulation in enumerate(simulations):
            assert set(simulation.tags.items()) == set(expected_tags[i].items())
            assert simulation.task.parameters == expected_tags[i]

    # can add a multi-parameter sweep definition with arguments
    def test_add_multiple_parameter_sweep_definition_with_arguments(self):
        builder = SimulationBuilder()

        def sweep_function(simulation, arg1, arg2):
            simulation.task.set_parameter('arg1', arg1)
            simulation.task.set_parameter('arg2', arg2)
            return {'arg1': arg1, 'arg2': arg2}

        builder.add_multiple_parameter_sweep_definition(sweep_function, [1, 2], [3, 4])
        assert len(builder) == 4
        expected_results = [{'arg1': 1, 'arg2': 3},
                            {'arg1': 1, 'arg2': 4},
                            {'arg1': 2, 'arg2': 3},
                            {'arg1': 2, 'arg2': 4}]
        for i, sweep in enumerate(builder):
            assert sweep[0].keywords == expected_results[i]
        simulations = self.get_simulations_with_builder(builder)
        for i, simulation in enumerate(simulations):
            assert simulation.task.parameters == expected_results[i]

    # can add a multi-parameter sweep definition with keyword arguments
    def test_add_multiple_parameter_sweep_definition_with_kwargs_in_dict(self):
        builder = SimulationBuilder()

        def sweep_function(simulation, sweep1, sweep2):
            simulation.task.set_parameter('arg1', sweep1)
            simulation.task.set_parameter('arg2', sweep2)
            return {'arg1': sweep1, 'arg2': sweep2}

        test_kwargs = {'sweep1': [1, 2, 3], 'sweep2': ['a', 'b', 'c']}
        builder.add_multiple_parameter_sweep_definition(sweep_function, **test_kwargs)
        assert len(builder) == len(test_kwargs['sweep1']) * len(test_kwargs['sweep2']) == 9

        expected_values = list(itertools.product(test_kwargs['sweep1'], test_kwargs['sweep2']))
        expected_results = []
        expected_tags = []
        for expected_value in expected_values:
            expected_results.append({'sweep1': expected_value[0], 'sweep2': expected_value[1]})
            expected_tags.append({'arg1': expected_value[0], 'arg2': expected_value[1]})

        for i, sweep in enumerate(builder):
            assert sweep[0].keywords == expected_results[i]

        simulations = self.get_simulations_with_builder(builder)
        for i, simulation in enumerate(simulations):
            assert simulation.tags == expected_tags[i]
            assert simulation.task.parameters == expected_tags[i]

    # can add a multi-parameter sweep definition with keyword arguments
    def test_add_multiple_parameter_sweep_definition_with_kwargs(self):
        builder = SimulationBuilder()

        def sweep_function(simulation, sweep1, sweep2):
            simulation.task.set_parameter('arg1', sweep1)
            simulation.task.set_parameter('arg2', sweep2)
            return {'arg1': sweep1, 'arg2': sweep2}

        test_kwargs = {'sweep1': [1, 2, 3], 'sweep2': ['a', 'b', 'c']}
        builder.add_multiple_parameter_sweep_definition(sweep_function, sweep1=test_kwargs['sweep1'],
                                                        sweep2=test_kwargs['sweep2'])
        assert len(builder) == len(test_kwargs['sweep1']) * len(test_kwargs['sweep2']) == 9

        expected_values = list(itertools.product(test_kwargs['sweep1'], test_kwargs['sweep2']))
        expected_results = []
        expected_tags = []
        for expected_value in expected_values:
            expected_results.append({'sweep1': expected_value[0], 'sweep2': expected_value[1]})
            expected_tags.append({'arg1': expected_value[0], 'arg2': expected_value[1]})

        for i, sweep in enumerate(builder):
            assert sweep[0].keywords == expected_results[i]

        simulations = self.get_simulations_with_builder(builder)
        for i, simulation in enumerate(simulations):
            assert simulation.tags == expected_tags[i]
            assert simulation.task.parameters == expected_tags[i]

    # raises a ValueError when adding a multi-argument sweep definition with no simulation argument
    def test_raises_value_error_with_no_simulation_argument(self):
        builder = SimulationBuilder()

        def sweep_function(arg1, arg2):
            return {'arg1': arg1, 'arg2': arg2}

        with pytest.raises(ValueError) as context:
            builder.add_multiple_parameter_sweep_definition(sweep_function, arg1=[1, 2, 3], arg2=[4, 5, 6])
        assert context.value.args[
                   0] == "The callback function passed to SweepBuilder.add_sweep_definition needs to take a simulation argument!"

    # Test cases to pass single dict item to add_multiple_parameter_sweep_definition:
    def test_add_multiple_parameter_sweep_definition_dict(self):

        # # Case1: len(args) = 1
        with self.subTest("test_args_len_eqs_1"):
            def sweep_function(simulation, a):
                simulation.task.set_parameter("param_a", a)
                return {"param_a": a}

            test_dict = {"a": "test"}
            builder = SimulationBuilder()
            builder.add_multiple_parameter_sweep_definition(sweep_function, test_dict)
            simulations = self.get_simulations_with_builder(builder)
            # Test if we have correct number of simulations
            expected_values = list(itertools.product([test_dict['a']]))
            assert len(simulations) == len(expected_values) == 1

            # Verify simulations individually
            expected_dict = {"param_a": "test"}
            assert simulations[0].task.parameters == expected_dict

        # Case2: len(kwargs) = 1
        with self.subTest("test_kwargs_len_eqs_1"):
            def sweep_function(simulation, test_dict):
                simulation.task.set_parameter("param_a", test_dict)
                return {"param_a": test_dict}

            builder = SimulationBuilder()
            builder.add_multiple_parameter_sweep_definition(sweep_function, test_dict={"a": "b"})
            simulations = self.get_simulations_with_builder(builder)
            # Test if we have correct number of simulations
            assert len(simulations) == 1
            expected_dict = {'param_a': {'a': 'b'}}
            assert simulations[0].task.parameters == expected_dict

    def test_add_sweep_definition_with_pandas_args(self):
        builder = SimulationBuilder()

        data = {
            "arg1": [420, 380, 390],
            "arg2": [50, 40, 45]
        }

        def sweep_function(simulation, df):
            simulation.task.set_parameter('arg1', df['arg1'])
            simulation.task.set_parameter('arg2', df['arg2'])
            return {'arg1': df['arg1'], 'arg2': df['arg2']}

        builder.add_sweep_definition(sweep_function, pd.DataFrame(data))
        assert builder.count == 1
        simulations = self.get_simulations_with_builder(builder)
        assert simulations[0].task.parameters['arg1'].equals(pd.DataFrame(data)['arg1'])
        assert simulations[0].task.parameters['arg2'].equals(pd.DataFrame(data)['arg2'])

    def test_add_sweep_definition_with_pandas_kwargs(self):
        builder = SimulationBuilder()

        data = {
            "arg1": [420, 380, 390],
            "arg2": [50, 40, 45]
        }

        def sweep_function(simulation, df):
            simulation.task.set_parameter('arg1', df['arg1'])
            simulation.task.set_parameter('arg2', df['arg2'])
            return {'arg1': df['arg1'], 'arg2': df['arg2']}

        builder.add_sweep_definition(sweep_function, df=pd.DataFrame(data))
        assert builder.count == 1
        simulations = self.get_simulations_with_builder(builder)
        assert simulations[0].task.parameters['arg1'].equals(pd.DataFrame(data)['arg1'])
        assert simulations[0].task.parameters['arg2'].equals(pd.DataFrame(data)['arg2'])

