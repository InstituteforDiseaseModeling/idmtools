from idmtools_local.core import RunTask
from interfaces import IPlatform, IExperiment


class ExperimentManager:
    """
    Manages an experiment.
    """

    def __init__(self, experiment: IExperiment, platform: IPlatform):
        """
        Constructor
        Args:
            experiment: The experiment to manage
        """
        self.platform = platform
        self.experiment = experiment

    def create_simulations(self):
        if not self.experiment.simulations:
            raise Exception("No simulations to run")

        for simulation in self.experiment.simulations:
            simulation.gather_assets()
            self.platform.create_simulation(simulation)

    def run(self):
        # Create experiment
        self.platform.create_experiment(self.experiment)

        # Execute the builder if present
        if self.experiment.builder:
            self.experiment.execute_builder()

        print(self.experiment)

        # Create the simulations based on builder
        self.create_simulations()

        # Run
        self.platform.run_simulation(self.experiment.simulations[0])

        for s in self.experiment.simulations:
            print(s)
            print(s.tags)
            RunTask.send(f"python ./Assets/model.py config.json", self.experiment.uid, s.uid)
