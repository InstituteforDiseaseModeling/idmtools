import allure
from typing import Dict
from unittest import TestCase

import pytest

from idmtools.builders import SimulationBuilder
from idmtools.entities.command_task import CommandTask
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations


def print_sweep(simulation: Simulation, value) -> Dict:
    print(value)
    return dict()


@pytest.mark.tasks
@pytest.mark.smoke
@allure.story("Sweeps")
@allure.suite("idmtools_core")
class TestTemplatedSimulation(TestCase):

    def test_generator(self):
        ts = TemplatedSimulations(base_task=CommandTask(command='ls'))
        builder = SimulationBuilder()
        total = 10
        builder.add_sweep_definition(print_sweep, range(total))
        ts.add_builder(builder)
        sims = [s for s in ts.simulations()]
        self.assertEqual(len(sims), total)

        # we can loop multiple times
        sims = [s for s in ts]
        self.assertEqual(len(sims), total)

        sims = [s for s in ts]
        self.assertEqual(len(sims), total)
