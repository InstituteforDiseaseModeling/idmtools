import time
from functools import partial
from unittest import TestCase

import allure
from idmtools.builders import SimulationBuilder
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment


@allure.story("Core")
@allure.suite("idmtools_core")
class TestPerformance(TestCase):
    def test_id_generation(self):
        task = CommandTask('echo')
        task.config = {}
        sb = SimulationBuilder()
        def dummy_hook(simulation, param, value):
            simulation.task.config[param] = value
            return {param: value}
        sb.add_sweep_definition(partial(dummy_hook, param='a'), range(200000))
        exp = Experiment.from_builder(sb, task)
        start = time.time()
        exp.simulations = list(exp.simulations)
        end = time.time()
        print(f'{end-start}s')