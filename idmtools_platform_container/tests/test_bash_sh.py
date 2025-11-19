import os
import shutil
import subprocess
import textwrap
import unittest
from functools import partial
from pathlib import Path
from typing import Any, Dict

from jinja2 import Template

from idmtools.builders import SimulationBuilder
from idmtools.core import EntityStatus
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask



class TestRunShTemplate(unittest.TestCase):
    output_dir = Path("generated_scripts")

    def generate_dynamic_script(self, a, c, output_dir):
        """Generate a dynamic Python script based on a, c and return its path."""
        template_str = textwrap.dedent("""\
    import os

    current_dir = os.path.abspath(os.getcwd())

    if __name__ == "__main__":
        import json
        parameters = {}
        with open("config.json", 'r') as fp:
            config = json.load(fp)
            parameters = config["parameters"]

        if config['parameters']['c'] == 1 and config['parameters']['a'] == 1:
            exit(-1)
        elif config['parameters']['c'] == 2 and config['parameters']['a'] == 2:
            exit(127)
        else:
            result = int(parameters["a"]) + int(parameters["b"])
            output_dir = os.path.join(current_dir, "output")
            if not os.path.exists(output_dir):
                os.mkdir(output_dir)
            with open(os.path.join(output_dir, "result.txt"), "w") as fp:
                fp.write("result:")
                fp.write(str(result))
""")

        tmpl = Template(template_str, trim_blocks=True, lstrip_blocks=True)
        code = tmpl.render(a=a, c=c)

        script_path = os.path.join(output_dir, f"generated_model_a{a}_c{c}.py")
        with open(script_path, "w") as f:
            f.write(code)
        return script_path

    def create_experiment(self, a=1, b=1, c=0, retries=None, wait_until_done=False):
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)
        generated_script_path = self.generate_dynamic_script(a, c, self.output_dir)
        task = JSONConfiguredPythonTask(
            script_path=generated_script_path,
            envelope="parameters",
            parameters=dict(a=a, b=b, c=c)
        )
        task.python_path = "python3"

        ts = TemplatedSimulations(base_task=task)
        builder = SimulationBuilder()

        def param_update(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
            return simulation.task.set_parameter(param, value)

        builder.add_sweep_definition(partial(param_update, param="a"), range(a))
        builder.add_sweep_definition(partial(param_update, param="b"), range(b))
        ts.add_builder(builder)

        # Now we can create our Experiment using our template builder
        experiment = Experiment.from_template(ts, name="test_experiment")
        experiment.run(wait_until_done=wait_until_done, retries=retries)
        return experiment

    @classmethod
    def setUpClass(cls) -> None:
        cls.job_directory = "DEST"
        cls.platform = Platform('Container', job_directory=cls.job_directory)

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.output_dir.exists():
            shutil.rmtree(cls.output_dir, ignore_errors=True)

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName


    def test_exit_0(self):
        experiment = self.create_experiment(a=3, b=3, c=0, wait_until_done=True)
        self.assertEqual(len(experiment.simulations), 9)
        self.assertEqual(experiment.succeeded, True)


    def test_exit_255(self):
        experiment = self.create_experiment(a=3, b=3, c=1, wait_until_done=True)
        self.assertEqual(experiment.succeeded, False)
        falied_simulations = experiment.get_simulations_by_tags(
            status=EntityStatus.FAILED, entity_type=True)
        self.assertEqual(len(experiment.simulations), 9)
        self.assertEqual(len(falied_simulations), 3)
        for failed_sim in falied_simulations:
            self.assertEqual(failed_sim.status, EntityStatus.FAILED)
            self.assertEqual(failed_sim.tags['a'], 1)

    def test_exit_negative_1(self):
        experiment = self.create_experiment(a=3, b=3, c=2, wait_until_done=True)
        self.assertEqual(experiment.succeeded, False)
        falied_simulations = experiment.get_simulations_by_tags(
            status=EntityStatus.FAILED, entity_type=True)
        self.assertEqual(len(experiment.simulations), 9)
        self.assertEqual(len(falied_simulations), 3)
        for failed_sim in falied_simulations:
            self.assertEqual(failed_sim.status, EntityStatus.FAILED)
            self.assertEqual(failed_sim.tags['a'], 2)




if __name__ == "__main__":
    unittest.main()
