import os
from functools import partial
from typing import Any, Dict, Iterable, Optional, Tuple

from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask


# --- Shared helpers -----------------------------------------------------------

def _assets_dir() -> str:
    current_dir = os.path.join(os.path.dirname(__file__))
    return os.path.join(current_dir, "..", "python_model", "inputs", "python", "Assets")

def _make_task(assets_directory: str,
               script_name: str = "model.py",
               base_params: Optional[Dict[str, Any]] = None,
               python_path: str = "python3") -> JSONConfiguredPythonTask:
    if base_params is None:
        base_params = dict(c=0)
    task = JSONConfiguredPythonTask(
        script_path=os.path.join(assets_directory, script_name),
        parameters=base_params
    )
    task.python_path = python_path
    return task

def _apply_sweeps(ts: TemplatedSimulations,
                  sweep_a: Iterable[int] = range(3),
                  sweep_b: Iterable[int] = range(5)) -> None:
    builder = SimulationBuilder()

    def param_update(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
        # Return value is merged into task config by idmtools
        return simulation.task.set_parameter(param, value)

    builder.add_sweep_definition(partial(param_update, param="a"), list(sweep_a))
    builder.add_sweep_definition(partial(param_update, param="b"), list(sweep_b))
    ts.add_builder(builder)

def _build_experiment(assets_directory: str,
                      exp_name: str = "python example") -> Experiment:
    task = _make_task(assets_directory)
    ts = TemplatedSimulations(base_task=task)
    ts.base_simulation.tags['sim_tag'] = "test_tag"
    _apply_sweeps(ts)

    experiment = Experiment.from_template(ts, name=exp_name)
    experiment.tags["tag1"] = 1
    experiment.assets.add_directory(assets_directory=assets_directory)
    return experiment


# --- helper function to create experiment and run it ------------

def create_experiment(platform: Platform,
                      use_suite: bool = True,
                      suite_name: str = "Idm Suite",
                      suite_tags: Optional[Dict[str, Any]] = None,
                      exp_name: str = "python example",
                      exp_tags: Optional[Dict[str, Any]] = None,
                      wait_until_done: bool = True
                      ) -> Tuple[Experiment, Optional[Suite]]:
    """
    Create and run an idmtools Experiment, optionally inside a Suite.

    Returns (experiment, suite_or_None)
    """
    assets_directory = _assets_dir()
    experiment = _build_experiment(assets_directory, exp_name=exp_name)

    if use_suite:
        suite = Suite(name=suite_name)
        if suite_tags:
            suite.update_tags(suite_tags)
        # Create the suite on the platform and attach the experiment
        platform.create_items([suite])
        suite.add_experiment(experiment)
        # Run via Suite (mirrors your original with-suite behavior)
        suite.run(platform=platform, wait_until_done=wait_until_done)
        return experiment, suite
    else:
        # Run experiment directly (mirrors your original without-suite behavior)
        experiment.run(platform=platform, wait_until_done=wait_until_done)
        return experiment, None


# --- Script entrypoint --------------------------------------------------------

if __name__ == "__main__":
    platform = Platform("Container", job_directory="DEST")

    # Equivalent to your original "with suite"
    exp, suite = create_experiment(
        platform,
        use_suite=True,
        suite_name="Idm Suite",
        suite_tags={'name': 'suite_tag', 'idmtools': '123'},
        exp_name="python example",
        wait_until_done=True
    )
    print(exp)
