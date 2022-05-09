import json
from pathlib import Path
from typing import Any, Dict, List

from idmtools.core.interfaces.ientity import IEntity

from idmtools.core import ItemType

from idmtools.core.interfaces import metadata_operations


class JSONMetadataOperations(metadata_operations.MetadataOperations):

    METADATA_FILENAME = 'metadata.json'

    def __init__(self, metadata_directory_root):
        self.metadata_directory_root = metadata_directory_root

    def _get_metadata_filepath(self, item: IEntity, item_type: ItemType = ItemType.SIMULATION) -> Path:
        sim_id = exp_id = suite_id = None
        if item_type is ItemType.SIMULATION:
            sim_id = item.uid
            exp = item.parent
            exp_id = exp.uid
            suite = exp.parent
            suite_id = suite.uid
        elif item_type is ItemType.EXPERIMENT:
            exp_id = item.uid
            suite = item.parent
            suite_id = suite.uid
        elif item_type is ItemType.SUITE:
            suite_id = item.uid

        filepath = Path(self.metadata_directory_root, *[id for id in [suite_id, exp_id, sim_id] if id is not None],
                        self.METADATA_FILENAME)
        self._initialize_file(item=item, item_type=item_type)
        return filepath

    def _initialize_file(self, item: IEntity, item_type: ItemType = ItemType.SIMULATION) -> bool:
        """
        Ensures that the directory containing a metadata file to-be exists and then creates the file with blank data
        if the file does not already exist
        Args:
            item: A simulation, experiment, or suite object
            item_type: the type of item that "item" is

        Returns: True if the file was created and set, False if it already existed
        """
        filepath = self._get_metadata_filepath(item=item, item_type=item_type)
        if filepath.exists():
            ret = False
        else:
            filepath.parent.mkdir(parents=True)
            self.set(item=item, item_type=item_type, metadata={})
            ret = True
        return ret

    @staticmethod
    def _get_by_filepath(filepath: Path) -> Dict[Any, Any]:
        with filepath.open(mode='r') as f:
            metadata = json.load(f)
        return metadata

    def get(self, item: IEntity, item_type: ItemType = ItemType.SIMULATION) -> Dict[Any, Any]:
        """
        Obtain all metadata for the given item
        Args:
            item: the item to retrieve metadata from
            item_type: the type of item that "item" is

        Returns: a key/value dict of metadata from the given item
        """
        filepath = self._get_metadata_filepath(item=item, item_type=item_type)
        return self._get_by_filepath(filepath=filepath)

    def set(self, item: IEntity, metadata: Dict[Any, Any], item_type: ItemType = ItemType.SIMULATION) -> Dict[Any, Any]:
        """
        Apply the given metadata to the specified item, overwriting any existing metadata key/values.
        Args:
            item: the item to set metadata on
            metadata: the metadata key/value pairs to set on the item
            item_type: the type of item that "item" is

        Returns: a key/value dict of fully-updated metadata from the given item
        """
        filepath = self._get_metadata_filepath(item=item, item_type=item_type)
        with filepath.open(mode='w') as f:
            json.dump(metadata, f)
        return metadata

    def update(self, item: IEntity, metadata: Dict[Any, Any], item_type: ItemType = ItemType.SIMULATION) \
            -> Dict[Any, Any]:
        """
        Apply the given metadata to the specified item, overwriting any existing, matching metadata key/values.
        This is effectively a union between the old and new metadata, with conflicts resolved in favor of the new
        metadata.
        Args:
            item: the item to update metadata on
            metadata: the metadata key/value pairs to add/modify on the item
            item_type: the type of item that "item" is

        Returns: a key/value dict of fully-updated metadata from the given item
        """
        existing_metadata = self.get(item=item, item_type=item_type)
        metadata = {**metadata, **existing_metadata}
        return self.set(item=item, item_type=item_type, metadata=metadata)

    def clear(self, item: IEntity, item_type: ItemType = ItemType.SIMULATION) -> Dict[Any, Any]:
        """
        Delete/empty the metadata for the given item
        Args:
            item: the item to clear metadata from
            item_type: the type of item that "item" is

        Returns: a key/value dict of fully-updated metadata from the given item
        """
        return self.set(item=item, item_type=item_type, metadata={})

    def _get_all_filepaths_of_item_type(self, item_type: ItemType = ItemType.SIMULATION) -> Dict[str, Path]:
        root = Path(self.metadata_directory_root)
        if item_type is ItemType.SIMULATION:
            glob = f"*/*/*/{self.METADATA_FILENAME}"
        elif item_type is ItemType.EXPERIMENT:
            glob = f"*/*/{self.METADATA_FILENAME}"
        elif item_type is ItemType.SUITE:
            glob = f"*/{self.METADATA_FILENAME}"
        else:
            raise metadata_operations.MetadataException(f"Unknown item type for metadata operation: {item_type}")
        metadata_filepaths = root.glob(pattern=glob)
        ids = [path.parent.name for path in metadata_filepaths]
        return dict(zip(ids, metadata_filepaths))

    def filter(self, filter: Dict[Any, Any], item_type: ItemType = ItemType.SIMULATION) -> List[str]:
        """
        Obtain all items that match the given metadata key/value pairs passed. Filters are currently expected to be
        'equal to' comparisons (key==value) with boolean operator AND between them all.
        Args:
            filter: a dict of metadata_key/value pairs for exact match searching
            item_type: the type of items to search for matches (simulation, experiment, suite, etc)

        Returns: a list of matching item ids # ck4, updated this to return ids, as not sure how to make proper items
        """
        filepaths = self._get_all_filepaths_of_item_type(item_type=item_type)
        item_ids = []
        for id, filepath in filepaths.items():
            metadata = self._get_by_filepath(filepath=filepath)
            filter_match = [(k in metadata) and (metadata[k] == v) for k, v in filter.items()]
            if all(filter_match):
                item_ids.append(id)
        return item_ids
