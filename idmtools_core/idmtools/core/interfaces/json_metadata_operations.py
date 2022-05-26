import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from idmtools.core.interfaces.ientity import IEntity

from idmtools.core import ItemType

from idmtools.core.interfaces import imetadata_operations
from idmtools.utils.json import IDMJSONEncoder


@dataclass
class JSONMetadataOperations(imetadata_operations.IMetadataOperations):

    METADATA_FILENAME = 'metadata.json'

    def __init__(self, metadata_directory_root):
        self.metadata_directory_root = metadata_directory_root

    def _get_metadata_filepath(self, item: IEntity) -> Path:
        sim_id = exp_id = suite_id = None
        if item.item_type is ItemType.SIMULATION:
            sim_id = item.uid
            exp = item.parent
            exp_id = exp.uid
            suite = exp.parent
            suite_id = suite.uid
        elif item.item_type is ItemType.EXPERIMENT:
            exp_id = item.uid
            suite = item.parent
            suite_id = suite.uid
        elif item.item_type is ItemType.SUITE:
            suite_id = item.uid
        else:
            raise imetadata_operations.MetadataException(f"Unknown item type: {item.item_type}")

        filepath = Path(self.metadata_directory_root, *[id for id in [suite_id, exp_id, sim_id] if id is not None],
                        self.METADATA_FILENAME)
        return filepath

    @staticmethod
    def _read_metadata_file(filepath: Path) -> Dict[Any, Any]:
        with filepath.open(mode='r') as f:
            metadata = json.load(f)
        return metadata

    @staticmethod
    def _write_metadata_file(item: IEntity, filepath: Path):
        to_dump = {} if item is None else item.to_dict()
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with filepath.open(mode='w') as f:
            json.dump(to_dump, f, cls=IDMJSONEncoder)

    def get(self, item: IEntity) -> Dict[Any, Any]:
        """
        Obtain all metadata for the given item
        Args:
            item: the item to retrieve metadata from
            item_type: the type of item that "item" is

        Returns: a key/value dict of metadata from the given item
        """
        filepath = self._get_metadata_filepath(item=item)
        try:
            metadata = self._read_metadata_file(filepath=filepath)
        except FileNotFoundError as e:
            e.args = [f"No metadata for item uid: {item.uid} type: {item.item_type}"]
            raise e
        return metadata

    def set(self, item: IEntity) -> None:
        """
        Apply the given metadata to the specified item, overwriting any existing metadata key/values.
        Args:
            item: the item to set metadata on

        Returns: Nothing
        """
        filepath = self._get_metadata_filepath(item=item)
        self._write_metadata_file(item=item, filepath=filepath)

    def clear(self, item: IEntity) -> None:
        """
        Delete/empty the metadata for the given item
        Args:
            item: the item to clear metadata from

        Returns: Nothing
        """
        filepath = self._get_metadata_filepath(item=item)
        if not filepath.exists():
            raise FileNotFoundError(f"No metadata exists to clear, item uid: {item.uid} type: {item.item_type}")
        self._write_metadata_file(item=None, filepath=filepath)

    @staticmethod
    def _matches_properties(properties, metadata):
        return all([(k in metadata) and (metadata[k] == v) for k, v in properties.items()])

    @staticmethod
    def _matches_tags(tags, metadata):
        tag_key = 'tags'
        is_match = all([(tag_key in metadata) and (k in metadata[tag_key]) and (metadata[tag_key][k] == v)
                        for k, v in tags.items()])
        return is_match

    def _matches_requirements(self, properties, tags, metadata):
        return self._matches_properties(properties=properties, metadata=metadata) and self._matches_tags(tags=tags, metadata=metadata)

    def filter_items(self, items: List[IEntity], properties: Dict[Any, Any] = None, tags: Dict[Any, Any] = None) \
            -> List[IEntity]:
        """
        Obtain all items that match the given metadata key/value pairs passed. property/tag filters are currently
        expected to be 'equal to' comparisons (key==value) with boolean operator AND between them all.
        Args:
            items: the list of items to search through
            properties: a dict of metadata_key/value pairs for exact match searching (non-tags)
            tags: a dict of metadata_key/value pairs for exact match searching in tags

        Returns: a list of matching items if items
        """
        properties = {} if properties is None else properties
        tags = {} if tags is None else tags

        matches = []
        for item in items:
            metadata = self.get(item=item)
            if self._matches_requirements(properties=properties, tags=tags, metadata=metadata):
                matches.append(item)
        return matches

    def _find_all_metadata_uids_and_paths_of_type(self, item_type):
        if item_type is ItemType.SIMULATION:
            pattern = f"*/*/*/{self.METADATA_FILENAME}"
        elif item_type is ItemType.EXPERIMENT:
            pattern = f"*/*/{self.METADATA_FILENAME}"
        elif item_type is ItemType.SUITE:
            pattern = f"*/{self.METADATA_FILENAME}"
        else:
            raise imetadata_operations.MetadataException(f"Unknown item type: {item_type}")

        matching_paths = list(self.metadata_directory_root.glob(pattern))
        uids = [path.parent.name for path in matching_paths]
        return dict(zip(uids, matching_paths))

    def filter(self, item_type: ItemType, properties: Dict[Any, Any] = None, tags: Dict[Any, Any] = None) \
            -> List[str]:
        """
        Obtain all item uids of the given type that match the given metadata key/value pairs passed property/tag.
        property/tag filters are currently expected to be 'equal to' comparisons (key==value) with boolean operator AND
        between them all.
        Args:
            item_type: the type of items to search for matches (simulation, experiment, suite, etc)
            properties: a dict of metadata_key/value pairs for exact match searching (non-tags)
            tags: a dict of metadata_key/value pairs for exact match searching in tags

        Returns: a list of item uids
        """
        properties = {} if properties is None else properties
        tags = {} if tags is None else tags

        matches = []
        uid_paths = self._find_all_metadata_uids_and_paths_of_type(item_type=item_type)
        for uid, filepath in uid_paths.items():
            metadata = self._read_metadata_file(filepath=filepath)
            if self._matches_requirements(properties=properties, tags=tags, metadata=metadata):
                matches.append(uid)
        return matches
