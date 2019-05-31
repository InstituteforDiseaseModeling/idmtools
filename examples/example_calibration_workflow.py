from idmtools.entities.algorithms.DummyNPA import DummyNPA
from idmtools.workflows.steps.GenerateSamplesStep import GenerateSamplesStep

s = GenerateSamplesStep(next_point_algorithm=DummyNPA(), parameters=[{"a":1, "b":2}])
print(s.execute())