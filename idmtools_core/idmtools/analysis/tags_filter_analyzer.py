import os
from logging import getLogger

from idmtools.core.platform_factory import Platform
from idmtools.utils.filter_simulations import FilterItem
from idmtools.entities.ianalyzer import IAnalyzer
from idmtools.core import ItemType
from COMPS.Data import Experiment as COMPSExperiment
from idmtools_models.python import PythonExperiment

logger = getLogger(__name__)

# This tags analyzer is for test_sweep_* test cases with a, b, c tags and params


class TagsFilterAnalyzer(IAnalyzer):

    def __init__(self, filenames=None, output_path=None, **kwargs):
        super().__init__(filenames=filenames, parse=False, **kwargs)
        self.output_path = output_path or "output"
        self.p = Platform('COMPS2')

    def initialize(self):
        self.output_path = os.path.join(self.working_dir, self.output_path)
        os.makedirs(self.output_path, exist_ok=True)

    def get_sim_folder(self, item):
        """
        Concatenate the specified top-level output folder with the simulation ID.

        Args:
            item: A simulation output parsing thread.

        Returns:
            The name of the folder to download this simulation's output to.
        """
        return os.path.join(self.output_path, str(item.uid))

    def filter(self, simulation):
        # filter a particular sim from the analysis
        # exp_id = 'e5f2b1dc-7053-ea11-a2bf-f0921c167862'
        # exp = self.p.get_item(exp_id, ItemType.EXPERIMENT)
        # Retrieve the experiment used to generate simulation
        self.p = Platform('COMPS2')
        exps = self.p.get_parent_by_object(simulation)
        exp_uid = exps.uid
        python_exp_id = exps.parent_id
        print("parent id:" + str(python_exp_id))
        # exp = self.p.get_item(exp_uid, ItemType.EXPERIMENT)
        # python_exp_id = exp.id
        # exp = COMPSExperiment.get(id=python_exp_id)
        # exp_id = exp.id

        # sim to filter
        sim_id = 'e6f2b1dc-7053-ea11-a2bf-f0921c167862'
        self.p = Platform('COMPS2')
        sims = FilterItem.filter_item_by_id(self.p, python_exp_id, ItemType.EXPERIMENT, skip_sims=[sim_id])
        return sims

    def map(self, data, simulation):
        # sim_data = data[self.filenames[0]]
        # Create a folder for the current simulation/item
        sim_folder = self.get_sim_folder(simulation)
        os.makedirs(sim_folder, exist_ok=True)

        # Create the requested files
        for filename in self.filenames:
            file_path = os.path.join(sim_folder, os.path.basename(filename))

            with open(file_path, 'wb') as outfile:
                outfile.write(data[filename])

            logger.debug(f'Writing to path: {file_path}')

    def reduce(self, all_data):
        match_dict = {"b", 2}
        for sim, sim_data in all_data.items():
            [b] = sim_data['b'].unique()

            if b in match_dict:
                print(b)
                logger.debug(f'Param match: {b}')

