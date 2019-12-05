import pandas as pd
import numpy as np
import cudf
import timeit

pandas_df = pd.DataFrame({'a': np.random.randint(0, 100000000, size=100000000),
                          'b': np.random.randint(0, 100000000, size=100000000)})

cudf_df = cudf.DataFrame.from_pandas(pandas_df)

# Timing Pandas
# Output: 82.2 ms per loop
timeit.timeit(pandas_df.a.mean())

# Timing cuDF
# Output: 5.12 ms per loop
timeit.timeit(cudf_df.a.mean())