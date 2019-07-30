import pandas as pd
from itertools import product
from idmtools.builders import ExperimentBuilder


class CsvExperimentBuilder(ExperimentBuilder):
    """
    Represents an experiment builder
    """

    def __init__(self):
        super().__init__()
        self.SweepFunctions = []

    def add_sweeps_from_file(self, file_path, func_map={}, type_map={}, sep=","):
        df_sweeps = pd.read_csv(file_path, sep=sep)

        row_count = df_sweeps.shape[0]
        for k in range(row_count):
            self.sweeps = []
            df = df_sweeps.iloc[[k]]

            # drop columns with nan
            df = df.dropna(axis=1)

            # make parameter with the correct value type
            type_map_t = {k: v for k, v in type_map.items() if k in df.columns.tolist()}
            df = df.astype(type_map_t)

            # make dict like: {'a': [1], 'b': [2]}
            sweep = df.to_dict(orient='list')

            # go through each (key, value)
            for param, value in sweep.items():
                # get the mapping function
                func = func_map[param]

                self.add_sweep_definition(func, value)

            self.SweepFunctions.extend(product(*self.sweeps))

    def __iter__(self):
        for tup in self.SweepFunctions:
            yield tup
