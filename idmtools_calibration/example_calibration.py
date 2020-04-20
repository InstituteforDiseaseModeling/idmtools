from CalibrationManager import CalibrationManager
from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from IKnob import MinMaxGuessKnob
from INextPointAlgorithm import INextPointAlgorithm

knobs = [
    MinMaxGuessKnob("parameter 1", 0, 10, 5),
    MinMaxGuessKnob("parameter 2", 0, 10, 5)
]

base_task = CommandTask('example')
base_task.config = dict(enable_births=False)
base_simulation = Simulation.from_task(base_task)

# Now we can create our Experiment using our template builder
experiment = Experiment(name="test", simulations=[base_simulation])
# Add our own custom tag to simulation
experiment.tags["tag1"] = 1

platform = Platform('LOCAL')

# The last step is to call run() on the ExperimentManager to run the simulations.
platform.run_items(experiment)
platform.wait_till_done(experiment)
# use system status as the exit code



def changes_in_model(base, knobs):
    pass


class SuperSimpleAlgorithm(INextPointAlgorithm):
    pass


algorithm = SuperSimpleAlgorithm()

calib = CalibrationManager(
    knobs=knobs,
    model_function=changes_in_model,
    algorithm=algorithm
)

calib.start()