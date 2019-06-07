from idmtools.workflows.calibration.steps.GenerateSamplesStep import GenerateSamplesStep
from idmtools.workflows.steps.RunSamples import RunSamples
from prettytable import PrettyTable


class CalibrationWorkflow:

    def __init__(self, parameters, next_point_algorithm, base_experiment, sample_to_simulation, platform):
        self.parameters = parameters
        self.base_experiment = base_experiment
        self.steps = [
            GenerateSamplesStep(next_point_algorithm=next_point_algorithm, parameters=parameters),
            RunSamples(base_experiment=self.base_experiment, builder_function=sample_to_simulation, platform=platform)
        ]
        self.printout = PrettyTable(["Step name", "Input"])

    def execute(self):
        previous_step_output = None
        for step in self.steps:
            print(f"Executing step {step.name}")
            if previous_step_output:
                step.set_inputs(previous_step_output)

            inputStr = str(previous_step_output)[:50] + "..." if len(str(previous_step_output)) > 50 else previous_step_output

            self.printout.add_row([step.name, inputStr])
            previous_step_output = step.execute()


        print(self.printout)
