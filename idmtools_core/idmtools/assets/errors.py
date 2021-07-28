"""
idmtools assets errors.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""


class DuplicatedAssetError(Exception):
    """
    DuplicatedAssetError is an error for when duplicates assets are added to collection.

    Notes:
        TODO: Add a doclink
    """

    def __init__(self, asset: 'TAsset'):  # noqa: F821
        """
        Initialize our error.

        Args:
            asset:Asset that caused the error
        """
        super().__init__(f"{asset} is already present in the collection!")
