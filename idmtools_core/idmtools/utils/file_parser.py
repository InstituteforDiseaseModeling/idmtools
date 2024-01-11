"""
File parser utility. Used to automatically load data.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import json
import os
from logging import getLogger
from typing import Dict

import pandas as pd

from io import StringIO, BytesIO

logger = getLogger(__name__)


class FileParser:
    """
    FileParser to load contents in analysis.
    """

    @classmethod
    def parse(cls, filename, content=None):
        """
        Parse filename and load the content.

        Args:
            filename: Filename to load
            content: Content to load

        Returns:
            Content loaded
        """
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
    def load_json_file(cls, filename, content) -> Dict:
        """
        Load JSON File.

        Args:
            filename: Filename to load
            content: Content

        Returns:
            JSOn as dict
        """
        return json.load(content)

    @classmethod
    def load_raw_file(self, filename, content):
        """
        Load content raw.

        Args:
            filename: Filename is none
            content: Content to load

        Returns:
            Content as it was
        """
        return content

    @classmethod
    def load_csv_file(cls, filename, content) -> pd.DataFrame:
        """
        Load csv file.

        Args:
            filename: Filename to load
            content: Content is loading

        Returns:
            Loaded csv file
        """
        if not isinstance(content, StringIO) and not isinstance(content, BytesIO):
            content = StringIO(content)

        csv_read = pd.read_csv(content, skipinitialspace=True)
        return csv_read

    @classmethod
    def load_xlsx_file(cls, filename, content) -> Dict[str, pd.ExcelFile]:
        """
        Load excel_file.

        Args:
            filename: Filename to load
            content: Content to load

        Returns:
            Loaded excel file
        """
        excel_file = pd.ExcelFile(content)
        return {sheet_name: excel_file.parse(sheet_name) for sheet_name in excel_file.sheet_names}

    @classmethod
    def load_txt_file(cls, filename, content):
        """
        Load text file.

        Args:
            filename: Filename to load
            content: Content to load

        Returns:
            Content
        """
        return str(content.getvalue().decode())

    @classmethod
    def load_bin_file(cls, filename, content):
        """
        Load a bin file.

        Args:
            filename: Filename to load
            content: Content to load

        Returns:
            Loaded bin file

        Notes:
            We should move this to a plugin in emodpy. We need to figure out how to structure that.
        """
        try:
            from idmtools_platform_comps.utils.spatial_output import SpatialOutput
            so = SpatialOutput.from_bytes(content.read(), 'Filtered' in filename)
            return so.to_dict()
        except ImportError as ex:
            logger.exception(ex)
            logger.error("Could not import item. Most likely dtk.tools is not installed")
