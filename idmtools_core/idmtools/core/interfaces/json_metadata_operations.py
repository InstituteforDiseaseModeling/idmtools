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
        self._initialize_file(filepath=filepath)
        return filepath

    @staticmethod
    def _read_metadata_file(filepath: Path) -> Dict[Any, Any]:
        with filepath.open(mode='r') as f:
            metadata = json.load(f)
        return metadata

    @staticmethod
    def _write_metadata_file(filepath: Path, data: Dict[Any, Any]):
        with filepath.open(mode='w') as f:
            json.dump(data, f)

    def _initialize_file(self, filepath: Path) -> bool:
        """
        Ensures that the directory containing a metadata file to-be exists and then creates the file with blank data
        if the file does not already exist
        Args:
            item: A simulation, experiment, or suite object
            item_type: the type of item that "item" is

        Returns: True if the file was created and set, False if it already existed
        """
        if filepath.exists():
            ret = False
        else:
            filepath.parent.mkdir(parents=True)
            self._write_metadata_file(filepath=filepath, data={})
            ret = True
        return ret

    def get(self, item: IEntity, item_type: ItemType = ItemType.SIMULATION) -> Dict[Any, Any]:
        """
        Obtain all metadata for the given item
        Args:
            item: the item to retrieve metadata from
            item_type: the type of item that "item" is

        Returns: a key/value dict of metadata from the given item
        """
        filepath = self._get_metadata_filepath(item=item, item_type=item_type)
        return self._read_metadata_file(filepath=filepath)

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
        self._write_metadata_file(filepath=filepath, data=metadata)
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
        metadata = {**existing_metadata, **metadata}
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

    def filter(self, items: List[IEntity], filter: Dict[Any, Any], item_type: ItemType = ItemType.SIMULATION) \
            -> List[IEntity]:
        """
        Obtain all items that match the given metadata key/value pairs passed. Filters are currently expected to be
        'equal to' comparisons (key==value) with boolean operator AND between them all.
        Args:
            items: the list of items to search through
            filter: a dict of metadata_key/value pairs for exact match searching
            item_type: the type of items to search for matches (simulation, experiment, suite, etc)

        Returns: a list of matching items
        """
        matches = []
        for item in items:
            metadata = self.get(item=item, item_type=item_type)
            filter_match = [(k in metadata) and (metadata[k] == v) for k, v in filter.items()]
            if all(filter_match):
                matches.append(item)
        return matches
