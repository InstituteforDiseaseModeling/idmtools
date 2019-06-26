import logging
import os
from logging import getLogger
from dramatiq import GenericActor, get_broker

from idmtools_local.config import DATA_PATH

logger = getLogger(__name__)


class AddAssetTask(GenericActor):
    """
    Allows to add assets either to the experiment assets or the simulation assets
    - If simulation_id is None -> experiment asset
    - Else simulation asset
    """
    class Meta:
        store_results = True
        max_retries = 0

    def perform(self, experiment_id, filename, path=None, contents=None, simulation_id=None):
        print(__name__)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('Adding assets for Experiment %s, simulation_id %s', experiment_id)
        path = os.path.join(DATA_PATH, experiment_id, simulation_id or "Assets", path or "", filename)

        # Sometimes, workers tries to create the same folder at the same time, silence the exception
        if not os.path.exists(os.path.dirname(path)):
            try:
                os.mkdir(os.path.dirname(path))
            except:
                pass

        with open(path, "wb") as fp:
            fp.write(bytes(contents, 'utf-8'))

broker = get_broker()
broker.declare_actor(AddAssetTask)