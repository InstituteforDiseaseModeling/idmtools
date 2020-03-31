import pandas as pd
import numpy as np
from numbers import Number
from itertools import product
from idmtools.builders import SimulationBuilder


class CsvExperimentBuilder(SimulationBuilder):
    """
    Class that represents an experiment builder.

    Examples:
        .. literalinclude:: ../examples/builders/csv_builder_python.py
    """

    def __init__(self):
        super().__init__()
        self.SweepFunctions = []

    def add_sweeps_from_file(self, file_path, func_map=None, type_map=None, sep=","):
        if type_map is None:
            type_map = {}
        if func_map is None:
            func_map = {}

        def strip_column(x):
            """
            strip white spaces for Number type column
            """
            y = x.strip() if not isinstance(x, Number) else x
            return np.nan if y == '' else y

        # make up our column converter
        convert_map = {c: strip_column for c, v in type_map.items() if v in (np.int, np.float, np.int64, np.float64)}

        # load csv with our converter
        # df_sweeps = pd.read_csv(file_path, sep=sep)
        df_sweeps = pd.read_csv(file_path, sep=sep, converters=convert_map)

        # go through each of rows
        row_count = df_sweeps.shape[0]
        for k in range(row_count):
            self.sweeps = []

            # get the current row as DataFrame
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
