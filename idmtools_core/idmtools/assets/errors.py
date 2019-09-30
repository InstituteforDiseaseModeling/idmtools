class DuplicatedAssetError(Exception):
    def __init__(self, asset: 'TAsset'):
        super().__init__(f"{asset} is already present in the collection!")
