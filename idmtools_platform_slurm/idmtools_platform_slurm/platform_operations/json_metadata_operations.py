"""
Here we implement the JSON Metadata operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
import json
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Type, Union
from dataclasses import dataclass, field
from idmtools.core import ItemType
from idmtools.core.interfaces import imetadata_operations
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.utils.json import IDMJSONEncoder
from idmtools_platform_slurm.platform_operations.utils import SlurmSuite, SlurmExperiment, SlurmSimulation

if TYPE_CHECKING:
    from idmtools_platform_slurm.slurm_platform import SlurmPlatform


@dataclass
class JSONMetadataOperations(imetadata_operations.IMetadataOperations):
    platform: 'SlurmPlatform'  # noqa: F821
    platform_type: Type = field(default=None)
    metadata_filename: str = field(default='metadata.json')

    @staticmethod
    def _read_from_file(filepath: Union[Path, str]) -> Dict:
        """
        Utility: read metadata from a file.
        Args:
            filepath: metadata file path
        Returns:
            JSON
        """
        filepath = Path(filepath)
        with filepath.open(mode='r') as f:
            metadata = json.load(f)
        return metadata

    @staticmethod
    def _write_to_file(filepath: Union[Path, str], data: Dict) -> None:
        """
        Utility: save metadata to a file.
        Args:
            filepath: metadata file path
            data: metadata as dictionary
        Returns:
            None
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with filepath.open(mode='w') as f:
            json.dump(data, f, cls=IDMJSONEncoder)

    def get_metadata_filepath(self, item: Union[Suite, Experiment, Simulation]) -> Path:
        """
        Retrieve item's metadata file path.
        Args:
            item: idmtools entity (Suite, Experiment and Simulation)
        Returns:
            item's metadata file path
        """
        if not isinstance(item, (Suite, Experiment, Simulation)):
            raise RuntimeError(f"get_metadata_filepath method supports Suite/Experiment/Simulation only.")
        item_dir = self.platform._op_client.get_directory(item)
        filepath = Path(item_dir, self.metadata_filename)
        return filepath

    def get(self, item: Union[Suite, Experiment, Simulation]) -> Dict:
        """
        Obtain item's metadata.
        Args:
            item: idmtools entity (Suite, Experiment and Simulation)
        Returns:
             key/value dict of metadata from the given item
        """
        if not isinstance(item, (Suite, Experiment, Simulation)):
            raise RuntimeError(f"Get method supports Suite/Experiment/Simulation only.")
        data = item.to_dict()
        if isinstance(item, Suite):
            data.pop('experiments', None)
        meta = json.loads(json.dumps(data, cls=IDMJSONEncoder))
        meta['id'] = meta['_uid']
        meta['uid'] = meta['_uid']
        meta['status'] = 'CREATED'
        meta['dir'] = os.path.abspath(self.platform.get_directory(item))

        if isinstance(item, Experiment):
            meta['suite_id'] = meta["parent_id"]
        elif isinstance(item, Simulation):
            meta['experiment_id'] = meta["parent_id"]

        return meta

    def dump(self, item: Union[Suite, Experiment, Simulation]) -> None:
        """
        Save item's metadata to a file.
        Args:
            item: idmtools entity (Suite, Experiment and Simulation)
        Returns:
            None
        """
        if not isinstance(item, (Suite, Experiment, Simulation)):
            raise RuntimeError(f"Dump method supports Suite/Experiment/Simulation only.")
        dest = self.get_metadata_filepath(item)
        meta = self.get(item)
        self._write_to_file(dest, meta)
        return meta

    def load(self, item: Union[Suite, Experiment, Simulation]) -> Dict:
        """
        Obtain item's metadata file.
        Args:
            item: idmtools entity (Suite, Experiment and Simulation)
        Returns:
             key/value dict of metadata from the given item
        """
        if not isinstance(item, (Suite, Experiment, Simulation)):
            raise RuntimeError(f"Load method supports Suite/Experiment/Simulation only.")
        meta_file = self.get_metadata_filepath(item)
        meta = self._read_from_file(meta_file)
        return meta

    def load_from_file(self, metadata_filepath: Union[Path, str]) -> Dict:
        """
        Obtain the metadata for the given filepath.
        Args:
            metadata_filepath: str
        Returns:
             key/value dict of metadata from the given filepath
        """
        if not Path(metadata_filepath).exists():
            raise RuntimeError(f"File not found: '{metadata_filepath}'.")
        meta = self._read_from_file(metadata_filepath)
        return meta

    def update(self, item: Union[Suite, Experiment, Simulation], metadata: Dict = {}, replace=True) -> None:
        """
        Update or replace item's metadata file.
        Args:
            item: idmtools entity (Suite, Experiment and Simulation.)
            metadata: dict to be updated or replaced
            replace: True/False
        Returns:
             None
        """
        if metadata is None:
            metadata = {}
        if not isinstance(item, (Suite, Experiment, Simulation)):
            raise RuntimeError(f"Set method supports Suite/Experiment/Simulation only.")
        meta = metadata
        if not replace:
            meta = self.load(item)
            meta.update(metadata)
        meta_file = self.get_metadata_filepath(item)
        self._write_to_file(meta_file, meta)

    def clear(self, item: Union[Suite, Experiment, Simulation]) -> None:
        """
        Clear the item's metadata file.
        Args:
            item: clear the item's metadata file
        Returns:
            None
        """
        if not isinstance(item, (Suite, Experiment, Simulation)):
            raise RuntimeError(f"Clear method supports Suite/Experiment/Simulation only.")
        self.update(item=item, metadata={}, replace=True)

    def get_children(self, item: Union[Suite, Experiment, SlurmSuite, SlurmExperiment]) -> List[Dict]:
        """
        Fetch item's children.
        Args:
            item: idmtools entity (Suite, SlurmSuite, Experiment, SlurmExperiment)
        Returns:
            Lis of metadata
        """
        if not isinstance(item, (Suite, SlurmSuite, Experiment, SlurmExperiment)):
            raise RuntimeError(f"Get children method supports [Slurm]Suite and [Slurm]Experiment only.")
        item_list = []
        item_dir = self.platform._op_client.get_directory_by_id(item.id, item.item_type)
        pattern = f'*/{self.metadata_filename}'
        for meta_file in item_dir.glob(pattern=pattern):
            meta = self.load_from_file(meta_file)
            item_list.append(meta)
        return item_list

    def get_all(self, item_type: ItemType) -> List[Dict]:
        """
        Obtain all the metadata for a given item type.
        Args:
            item_type: the type of metadata to search for matches (simulation, experiment, suite, etc)
        Returns:
            list of metadata with given item type
        """
        if item_type is ItemType.SIMULATION:
            pattern = f"*/*/*/{self.metadata_filename}"
        elif item_type is ItemType.EXPERIMENT:
            pattern = f"*/*/{self.metadata_filename}"
        elif item_type is ItemType.SUITE:
            pattern = f"*/{self.metadata_filename}"
        else:
            raise RuntimeError(f"Unknown item type: {item_type}")
        item_list = []
        root = Path(self.platform.job_directory)
        for meta_file in root.glob(pattern=pattern):
            meta = self.load_from_file(meta_file)
            item_list.append(meta)
        return item_list

    @staticmethod
    def _match_filter(item: Dict, metadata: Dict, ignore_none=True):
        """
        Utility: verify if item match metadata.
        Note: compare key/value if value is not None else just check key exists
        Args:
            item: dict represents metadata of Suite/Experiment/Simulation
            metadata: dict as a filter
            ignore_none: True/False (ignore None value or not)
        Returns:
            list of Dict items
        """
        for k, v in metadata.items():
            if ignore_none:
                if v is None:
                    is_match = k in item
                else:
                    is_match = k in item and item[k] == v
            else:
                if v is None:
                    is_match = k in item and item[k] is None
                else:
                    is_match = k in item and item[k] == v
            if not is_match:
                return False
        return True

    def filter(self, item_type: ItemType, property_filter: Dict = None, tag_filter: Dict = None,
               meta_items: List[Dict] = None, ignore_none=True) -> List[Dict]:
        """
        Obtain all items that match the given properties key/value pairs passed.
        The two filters are applied on item with 'AND' logical checking.
        Args:
            item_type: the type of items to search for matches (simulation, experiment, suite, etc)
            property_filter: a dict of metadata key/value pairs for exact match searching
            tag_filter: a dict of metadata key/value pairs for exact match searching
            meta_items: list of metadata
            ignore_none: True/False (ignore None value or not)
        Returns:
            a list of metadata matching the properties key/value with given item type
        """
        if meta_items is None:
            meta_items = self.get_all(item_type)
        item_list = []
        for meta in meta_items:
            is_match = True
            if property_filter:
                is_match = self._match_filter(meta, property_filter, ignore_none=ignore_none)
            if tag_filter:
                is_match = is_match and self._match_filter(meta['tags'], tag_filter, ignore_none=ignore_none)
            if is_match:
                item_list.append(meta)
        return item_list
