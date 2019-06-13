import numpy as np
import pandas as pd
from idmtools.builders import ArmExperimentBuilder
from idmtools.builders.ArmExperimentBuilder import SweepArm, ArmType


class CsvExperimentBuilder(ArmExperimentBuilder):
    """
    Represents an experiment builder
    """

    def __init__(self):
        super().__init__()

    def add_sweeps_from_file(self, file_path, func_map={}):

        # file_path = 'arm_funcs1.csv'
        df_sweeps = pd.read_csv(file_path, sep='\t')
        print(df_sweeps)

        for index, row in df_sweeps.iterrows():
            # print(row)
            df = pd.DataFrame(row)
            df = df.dropna()
            df = df.astype(np.int)
            d = df.to_dict()
            key = list(d.keys())[0]
            d_funcs = d[key]

            funcs = []
            for func, values in d_funcs.items():
                funcs.append((func_map[func], values))

            arm = SweepArm(ArmType.zip, funcs)
            self.add_arm(arm)

    def __iter__(self):
        for tup in self.sweep_definitions:
            yield tup
