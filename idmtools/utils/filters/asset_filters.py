def default_asset_file_filter(asset):
    patterns = [
        "__pycache__",
        ".pyc"
    ]
    return not any([p in asset.absolute_path for p in patterns])


def file_name_is(asset, filenames):
    return asset.filename in filenames


def asset_in_directory(asset, directories):
    return any([d in asset.absolute_path for d in directories])
