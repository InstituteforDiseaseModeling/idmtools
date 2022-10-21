from typing import Optional, List

import pandas as pd

from idmtools.entities import IAnalyzer
from idmtools.entities.ianalyzer import ANALYSIS_ITEM_MAP_DATA_TYPE, ANALYZABLE_ITEM, ANALYSIS_REDUCE_DATA_TYPE


class DownloadFilepathAnalyzer(IAnalyzer):

    def __init__(self, uid=None, working_dir: Optional[str] = None, parse: bool = True, filenames: Optional[List[str]] = None):
        super().__init__(uid, working_dir, parse, filenames)

    def map(self, data: ANALYSIS_ITEM_MAP_DATA_TYPE, item: ANALYZABLE_ITEM):
        df = pd.DataFrame.from_records([(x, y) for x, y in data.items()], columns=['filename', 'path'])
        df['id'] = str(item.id)
        return df

    def reduce(self, all_data: ANALYSIS_REDUCE_DATA_TYPE):
        DownloadFilepathAnalyzer.gdf = pd.concat(all_data.values())
        DownloadFilepathAnalyzer.gdf.to_csv("files.csv")
