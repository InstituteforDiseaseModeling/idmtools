import os
from idmtools.core import Platform
from idmtools.workflows.calibration import Parameter
from idmtools.workflows.calibration.CalibrationWorkflow import CalibrationWorkflow
from idmtools.workflows.calibration.algorithms.DummyNPA import DummyNPA
from idmtools_models.python import PythonExperiment


def sample_to_simulation(simulation, sample):
    for p in sample:
        simulation.set_parameter(p.name, p.value)

    return {p.name:p.value for p in sample.parameters}

experiment = PythonExperiment(name="My First experiment", model_path=os.path.join("work", "inputs", "simple_calibration", "model.py"))

s = CalibrationWorkflow(next_point_algorithm=DummyNPA(),
                        parameters=[Parameter(name="a", min=0, max=10, guess=3), Parameter(name="b", min=0, max=10, guess=1)],
                        base_experiment=experiment, sample_to_simulation=sample_to_simulation, platform=Platform('Local'))
s.execute()
