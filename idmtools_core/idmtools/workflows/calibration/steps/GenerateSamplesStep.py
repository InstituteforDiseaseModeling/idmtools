from idmtools.workflows.IWorkflowStep import IWorkflowStep


class GenerateSamplesStep(IWorkflowStep):
    def __init__(self, next_point_algorithm, parameters):
        super().__init__(name="Generate Samples")
        self.npa = next_point_algorithm
        self.parameters = parameters

    def execute(self):
        samples = self.npa.generate_samples(self.parameters, 10)
        return samples
