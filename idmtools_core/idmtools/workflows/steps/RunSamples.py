from idmtools.builders import SimulationBuilder
from idmtools.managers import ExperimentManager
from idmtools.workflows.IWorkflowStep import IWorkflowStep


class RunSamples(IWorkflowStep):
    def __init__(self, base_experiment, builder_function, platform):
        super().__init__(name="Run Samples")
        self.base_experiment = base_experiment
        self.builder_function = builder_function
        self.platform = platform

    def execute(self):
        builder = SimulationBuilder()
        builder.add_sweep_definition(self.builder_function, self.inputs)
        self.base_experiment.builder = builder

        em = ExperimentManager(experiment=self.base_experiment, platform=self.platform)
        em.run()
