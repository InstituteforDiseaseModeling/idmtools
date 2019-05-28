from dramatiq import group

from idmtools_local.core import CreateExperimentTask, CreateSimulationTask, RunTask, AddAssetTask
from entities.IExperiment import IExperiment
from entities.IPlatform import IPlatform
from entities.ISimulation import ISimulation


class LocalPlatform(IPlatform):
    """
    Represents the platform allowing to run simulations locally.
    """

    def create_experiment(self, experiment: IExperiment):
        m = CreateExperimentTask.send()
        eid = m.get_result(block=True)
        experiment.uid = eid
        self.send_assets_for_experiment(experiment)

    def send_assets_for_experiment(self, experiment):
        # Go through all the assets
        messages = []
        for asset in experiment.assets:
            messages.append(
                AddAssetTask.message(experiment.uid, asset.filename, path=asset.relative_path, contents=asset.content.decode("utf-8")))
        group(messages).run().wait()

    def send_assets_for_simulation(self, simulation):
        # Go through all the assets
        messages = []
        for asset in simulation.assets:
            messages.append(
                AddAssetTask.message(simulation.experiment_id, asset.filename, path=asset.relative_path,
                                     contents=asset.content.decode("utf-8"), simulation_id=simulation.uid))
        group(messages).run().wait()

    def create_simulations(self, experiment: IExperiment):
        for simulation in experiment.simulations:
            m = CreateSimulationTask.send(simulation.experiment.uid)
            sid = m.get_result(block=True)
            simulation.uid = sid
            self.send_assets_for_simulation(simulation)

    def run_simulations(self, experiment: IExperiment):
        for simulation in experiment.simulations:
            RunTask.send(simulation.experiment.command.cmd, simulation.experiment.uid, simulation.uid)
