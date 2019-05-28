from dramatiq import group

from idmtools_local.core import CreateExperimentTask, CreateSimulationTask, RunTask, AddAssetTask
from interfaces.IPlatform import IPlatform


class LocalPlatform(IPlatform):

    @staticmethod
    def create_experiment(experiment):
        m = CreateExperimentTask.send()
        eid = m.get_result(block=True)
        experiment.uid = eid

        # Go through all the assets
        messages = []
        for asset in experiment.assets:
            messages.append(AddAssetTask.message(experiment.uid, asset.filename, path=asset.relative_path, contents=asset.content))
        group(messages).run().wait()

    @staticmethod
    def create_simulation(simulation):
        m = CreateSimulationTask.send(simulation.experiment_id)
        sid = m.get_result(block=True)
        simulation.uid = sid

        # Go through all the assets
        messages = []
        for asset in simulation.assets:
            messages.append(
                AddAssetTask.message(simulation.experiment_id, asset.filename, path=asset.relative_path,
                                     contents=asset.content, simulation_id=simulation.uid))
        group(messages).run().wait()

    @staticmethod
    def run_simulation(simulation):
        RunTask.send(f"python ./Assets/model.py config.json", simulation.experiment_id, simulation.uid)