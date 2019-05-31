from idmtools.entities import IPlatform, IExperiment


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
        """
        Create all the simulations contained in the experiment on the platform.
        """
        if not self.experiment.simulations:
            raise Exception("No simulations to run")

        # Gather the assets
        for simulation in self.experiment.simulations:
            simulation.gather_assets()

        # Send the experiment to the platform
        self.platform.create_simulations(self.experiment)

    def run(self):
        """
        Main entry point of the manager.
        - Create the experiment
        - Execute the builder (if any) to generate all the simulations
        - Create the simulations on the platform
        - Trigger the run on the platform
        """
        # Create experiment
        self.platform.create_experiment(self.experiment)

        # Execute the builder if present
        if self.experiment.builder:
            self.experiment.execute_builder()

        print(self.experiment)

        # Create the simulations based on builder
        self.create_simulations()

        # Run
        self.platform.run_simulations(self.experiment)

        for simulation in self.experiment.simulations:
            print(simulation)
            print(simulation.tags)
