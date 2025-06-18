"""idmtools add analyzer.

More of an example.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
from idmtools.entities.ianalyzer import IAnalyzer, ANALYZABLE_ITEM


class AddAnalyzer(IAnalyzer):
    """
    A simple base class to add analyzers.

    Examples:
        .. literalinclude:: ../../examples/analyzers/example_analysis_AddAnalyzer.py
    """

    def __init__(self, filenames=None, output_path='output'):
        """
        Initialize our analyzer.

        Args:
            filenames: Filename to fetch
            output_path: Path to write output to
        """
        super().__init__()
        self.output_path = output_path
        self.filenames = filenames or []

        # We only want the raw files -> disable parsing
        self.parse = True

    def filter(self, item: ANALYZABLE_ITEM) -> bool:
        """
        Determine whether the given item should be included by this analyzer.

        This implementation accepts all items unconditionally.

        Args:
            item (ANALYZABLE_ITEM): The item to be evaluated.

        Returns:
            bool: Always returns True, meaning all items are accepted.
        """
        return True  # download them all!

    def initialize(self):
        """
        Initialize our analyzer before running it.

        We use this to create our output directory.

        Returns:
            None
        """
        self.output_path = os.path.join(self.working_dir, self.output_path)
        os.makedirs(self.output_path, exist_ok=True)

    def map(self, data, item: ANALYZABLE_ITEM):
        """
        Run this on each item and the files we retrieve.

        Args:
            data: Map of filesnames -> content
            item: Item we are mapping

        Returns:
            Values added up
        """
        number = int(list(data.values())[0].split()[10])
        result = number + 100
        return result

    # ck4, should we pass objects as the keys? e.g. Item-type, not just their id
    def reduce(self, data):
        """
        Combine all the data we mapped.

        Args:
            data: Map of results in form Item -> map results

        Returns:
            Sum of all the results
        """
        # data is currently a dict with item_id: value  entries
        value = sum(data.values())
        print(value)
        return value
