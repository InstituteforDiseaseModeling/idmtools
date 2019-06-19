import os
from dramatiq import GenericActor
from idmtools_local.core.Data import JobStatus
from idmtools_local.data import SimulationDatabase


class CreateSimulationTask(GenericActor):
    """
    Creates a simulation.
    - Create the simulation folder in the experiment_id parent folder
    - Returns the UUID of the newly created simulation folder
    """
    class Meta:
        store_results = True
        max_retries = 0

    def perform(self, experiment_id):
        print(__name__)
        import random
        import string
        uuid = ''.join(random.choice(string.digits + string.ascii_uppercase) for _ in range(5))

        simulation_status: JobStatus = JobStatus(uid=uuid, parent_uuid= experiment_id,
                                                 data_path=os.path.join("/data", experiment_id, uuid))
        SimulationDatabase.save(simulation_status)

        os.mkdir(os.path.join("/data", experiment_id, uuid))
        return uuid