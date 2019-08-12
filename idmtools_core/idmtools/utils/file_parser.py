import json
import os
import pandas as pd

from io import StringIO, BytesIO


class FileParser:
    @classmethod
    def parse(cls, filename, content=None):
        file_extension = os.path.splitext(filename)[1][1:].lower()
        content = BytesIO(content)

        if file_extension == 'json':
            return cls.load_json_file(filename, content)

        if file_extension == 'csv':
            return cls.load_csv_file(filename, content)

        if file_extension == 'xlsx':
            return cls.load_xlsx_file(filename, content)

        if file_extension == 'txt':
            return cls.load_txt_file(filename, content)

        if file_extension == 'bin' and 'SpatialReport' in filename:
            return cls.load_bin_file(filename, content)

        return cls.load_raw_file(filename, content)

    @classmethod
    def load_json_file(cls, filename, content):
        return json.load(content)

    @classmethod
    def load_raw_file(self, filename, content):
        return content

    @classmethod
    def load_csv_file(cls, filename, content):
        if not isinstance(content, StringIO) and not isinstance(content, BytesIO):
            content = StringIO(content)

        csv_read = pd.read_csv(content, skipinitialspace=True)
        return csv_read

    @classmethod
    def load_xlsx_file(cls, filename, content):
        excel_file = pd.ExcelFile(content)
        return {sheet_name: excel_file.parse(sheet_name) for sheet_name in excel_file.sheet_names}

    @classmethod
    def load_txt_file(cls, filename, content):
        return str(content.getvalue().decode())

    # ck4, does this belong here, or in a platform?
    @classmethod
    def load_bin_file(cls, filename, content):
        from dtk.tools.output.SpatialOutput import SpatialOutput
        so = SpatialOutput.from_bytes(content.read(), 'Filtered' in filename)
        return so.to_dict()
