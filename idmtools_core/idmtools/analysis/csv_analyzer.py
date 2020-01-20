import os
import pandas as pd
from idmtools.entities import IAnalyzer


class CSVAnalyzer(IAnalyzer):
    def __init__(self, filenames, parse=True):
        super().__init__(parse, filenames=filenames)
        if not all(['csv' in os.path.splitext(f)[1].lower() for f in self.filenames]):
            raise Exception('Please ensure all filenames provided to CSVAnalyzer have a csv extension.')

    def map(self, data, simulation):
        # return self.filenames
        # data[self.filenames[0]]

        concatenated_df = pd.concat(list(data.values()), axis=0, ignore_index=True, sort=True)
        return concatenated_df

        # dfs = [pd.read_csv(f, index_col=None) for f in data[self.filenames[0]]]
        # dfs = [pd.read_csv(f, index_col=None) for f in self.filenames]
        # common_cols = list(set.intersection(*[set(x.columns.tolist()) for x in dfs]))
        # sim_csv_data = pd.concat((df.set_index(common_cols) for df in dfs), axis=1).reset_index()
        # return sim_csv_data

        # # Dataframe for each file and concat
        # df_from_each_file = (pd.read_csv(filename, index_col=None, header=None) for filename in data[self.filenames[0]])
        # concatenated_df = pd.concat(df_from_each_file, axis=0, ignore_index=True)
        # return concatenated_df

        # # Try merge
        # files = data[self.filenames[0]]
        #
        # def get_merged(files, **kwargs):
        #     df = pd.read_csv(files[0], **kwargs)
        #     for f in files[1:]:
        #         df = df.merge(pd.read_csv(f, **kwargs), how='outer')
        #     return df
        #
        # csv_data = get_merged(files, index_col=None, header=0, axis=1, ignore_index=True)
        # return csv_data

        # # Read and concat csv
        # list = []
        # for filename in data[self.filenames[0]]:
        #     df = pd.read_csv(filename, index_col=None, header=0)
        #     list.append(df)
        # simdata = pd.concat(list, axis=0, ignore_index=True)
        # return simdata

        # # # Experiment with create headers first
        # csv_files = data[self.filenames[0]]
        # csv_separator = ','
        #
        # # run through files to define the common headers
        # col_headers = []
        # for filename in csv_files:
        #     with open(filename, 'r') as f:
        #         headers = f.readline().split(csv_separator)
        #         col_headers += col_headers + list(set(col_headers)) - set(headers)

    def reduce(self, all_data):

        # Let's hope the first simulation is representative
        first_sim = next(iter(all_data.keys()))
        exp_id = str(first_sim.experiment.uid)

        results = pd.concat(list(all_data.values()), axis=0,
                            keys=[str(k.uid) for k in all_data.keys()],
                            names=['SimId'])
        results.index = results.index.droplevel(1)  # Remove default index

        os.makedirs(exp_id, exist_ok=True)
        # NOTE: If running twice with different filename, the output files will collide
        results.to_csv(os.path.join(exp_id, self.__class__.__name__+'.csv'))


