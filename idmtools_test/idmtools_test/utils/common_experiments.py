import os

from idmtools.assets import AssetCollection
from idmtools.core import EntityStatus
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_test import COMMON_INPUT_PATH


def get_model_py_templated_experiment(case_name: str, default_parameters: dict = None,
                                      assets_path: str = os.path.join(COMMON_INPUT_PATH, "python", "Assets",
                                                                      "MyExternalLibrary"),
                                      relative_path="MyExternalLibrary", templated_simulations=None) -> Experiment:
    """
    Returns an experiment using inputs/python/model.py and a JSONConfiguredPythonTask as the task

    Args:
        case_name: Test case name
        default_parameters: Default parameters from model
        assets_path: Default path to assets
        relative_path: Relative path to add to assets
        templated_simulations:Optional override for templated simulations

    Returns:

    """
    from idmtools_models.python.json_python_task import JSONConfiguredPythonTask

    if default_parameters is None:
        default_parameters = dict()
    model_path = os.path.join(COMMON_INPUT_PATH, "python", "model.py")
    ac = AssetCollection()
    ac.add_directory(assets_directory=assets_path, relative_path=relative_path)
    task = JSONConfiguredPythonTask(script_path=model_path, envelope="parameters", parameters=default_parameters)
    if templated_simulations is None:
        templated_simulations = TemplatedSimulations(base_task=task)
    e = Experiment(name=case_name, simulations=templated_simulations, assets=ac)
    # assets=AssetCollection.from_directory(assets_directory=assets_path, relative_path="MyExternalLibrary"))
    e.tags = {"string_tag": "test", "number_tag": 123}
    return e


def get_model1_templated_experiment(case_name, parameters=None):
    from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
    if parameters is None:
        parameters = dict(c='c-value')
    model_path = os.path.join(COMMON_INPUT_PATH, "python", "model1.py")
    e = Experiment(name=case_name,
                   simulations=TemplatedSimulations(base_task=JSONConfiguredPythonTask(parameters=parameters,
                                                                                       script_path=model_path)
                                                    ))
    e.tags = {"string_tag": "test", "number_tag": 123, "KeyOnly": None}
    return e


def wait_on_experiment_and_check_all_sim_status(tc, experiment, platform=None,
                                                expected_status: EntityStatus = EntityStatus.SUCCEEDED,
                                                scheduling=False):
    """
    Run experiment and wait for it to finish then check all sims succeeded
    Args:
        tc: Test case(self)
        experiment: Experiment object
        platform: Platform
        expected_status: Expected status
    Returns:

    """
    experiment.run(wait_until_done=True, scheduling=scheduling, retries=5)
    if isinstance(tc, type):
        tc.assertTrue(tc, all([s.status == expected_status for s in experiment.simulations]))
    else:
        tc.assertTrue(all([s.status == expected_status for s in experiment.simulations]))
        if expected_status is EntityStatus.SUCCEEDED:
            tc.assertTrue(experiment.done)
            tc.assertTrue(experiment.succeeded)
        elif expected_status is EntityStatus.FAILED:
            tc.assertFalse(experiment.succeeded)
    return experiment
