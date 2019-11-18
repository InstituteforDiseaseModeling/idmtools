import os
import pandas as pd
from idmtools.entities import IAnalyzer

class CSVAnalyzer(IAnalyzer):
    def __init__(self, filenames, uid=None, working_dir=None, parse=True):
        super().__init__(uid, working_dir, parse, filenames=filenames)

    def filter(self, simulation: 'TSimulation') -> bool:
        #return int(simulation.tags.get("b")) > 5
        # NOTE: Only succeded simulations make it here, see:
        # https://github.com/InstituteforDiseaseModeling/idmtools/issues/457
        return True

    def map(self, data, simulation):
        if not all(['csv' in os.path.splitext(f)[1].lower() for f in self.filenames]):
            # TODO: Is this the right way to raise an exception in idmtools?
            raise Exception('Please ensure all filenames prived to CSVAnalyzer have a csv extension.')
        return data[self.filenames[0]]

    def reduce(self, all_data):
        # Let's hope the first simulation is representative
        first_sim = next(iter(all_data.keys()))
        exp_id = str(first_sim.experiment.uid)

        results = pd.concat(list(all_data.values()), axis=0,
            keys = [str(k.uid) for k in all_data.keys()],
            names = ['SimId'])
        results.index = results.index.droplevel(1) # Remove default index

        os.makedirs(exp_id, exist_ok=True)
        # NOTE: If running twice with different filename, the output files will collide
        results.to_csv( os.path.join( exp_id, self.__class__.__name__+'.csv') )
