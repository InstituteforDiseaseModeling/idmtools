"""
idmtools FileList classes.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from typing import List
import os
import re
from idmtools.assets import Asset, AssetCollection
from idmtools.utils.local_os import LocalOS


class FileList:
    """
    Special utility class to help handling user files.
    """

    def __init__(self, root=None, files_in_root=None, recursive=False, ignore_missing=False, relative_path=None,
                 max_depth=3):
        """
        Represents a set of files that are specified RELATIVE to root.

        e.g. /a/b/c.json could be : root: '/a' files_in_root: ['b/c.json']
        :param root: The dir all files_in_root are relative to.
        :param files_in_root: The listed files
        """
        self.files: List[Asset] = []
        self.ignore_missing = ignore_missing
        self.max_depth = max_depth

        # Make sure we have correct separator
        # os.path.normpath(f) would be best but is not working the same way on UNIX systems
        if files_in_root is not None:
            if LocalOS.is_window():
                files_in_root = [os.path.normpath(f) for f in files_in_root]
            else:
                files_in_root = [re.sub(r"[\\/]", os.sep, os.path.normpath(f)) for f in files_in_root]

        if root:
            self.add_path(path=root, files_in_dir=files_in_root, recursive=recursive, relative_path=relative_path)

    def add_asset_file(self, af):
        """
        Method used to add asset file.

        Args:
            af: asset file to add

        Returns: None
        """
        self.files.append(af)

    def add_file(self, path, relative_path=''):
        """
        Method used to add a file.

        Args:
            path: file oath
            relative_path: file relative path

        Returns: None
        """
        # If already present -> bypass
        for f in self.files:
            if f.absolute_path and os.path.abspath(f.absolute_path) == os.path.abspath(path):
                return

        if os.path.isdir(path):
            raise ValueError("%s is a directory. add_file is expecting a file!" % path)

        absolute_path = os.path.abspath(path)
        file_name = os.path.basename(path)
        try:
            af = Asset(filename=file_name, relative_path=relative_path, absolute_path=absolute_path)
            self.add_asset_file(af)
        except Exception as e:
            if not self.ignore_missing:
                raise e

    def add_path(self, path, files_in_dir=None, relative_path=None, recursive=False):
        """
        Add a path to the file list.

        Args:
            path: The path to add (needs to be a dictionary)
            files_in_dir: If we want to only retrieve certain files in this path
            relative_path: relative_path: The relative path prefixed to each added files
            recursive: Do we want to browse recursively

        Returns: None

        """
        # Little safety
        if not os.path.isdir(path) and not path.startswith('\\\\'):
            raise RuntimeError("add_path() requires a directory. '%s' is not." % path)

        if not recursive:
            if files_in_dir is None:
                files_in_dir = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

            for file_name in files_in_dir:
                file_path = os.path.join(path, file_name)
                f_relative_path = os.path.normpath(
                    file_path.replace(path, '').strip(os.sep).replace(os.path.basename(file_path), ''))
                if relative_path is not None:
                    f_relative_path = os.path.join(relative_path, f_relative_path)
                self.add_file(file_path, relative_path=f_relative_path)

        else:
            # Walk through the path
            for root, _subdirs, files in os.walk(path):
                # Little safety to not go too deep
                depth = root[len(path) + len(os.path.sep):].count(os.path.sep)
                if depth > self.max_depth:
                    continue

                # Add the files in the current dir
                for f in files:
                    # Find the file relative path compared to the root folder
                    # If the relative_path is . -> change it into ''
                    f_relative_path = os.path.normpath(os.path.relpath(root, path))
                    if f_relative_path == '.':
                        f_relative_path = ''

                    # if files_in_dir specified -> skip the ones not included
                    if files_in_dir is not None and f not in files_in_dir and os.path.join(f_relative_path,
                                                                                           f) not in files_in_dir:
                        continue

                    # if we want to force a relative path -> force it
                    if relative_path is not None:
                        f_relative_path = os.path.join(relative_path, f_relative_path)

                    # add the file
                    self.add_file(os.path.join(root, f), relative_path=f_relative_path)

    def to_asset_collection(self) -> AssetCollection:
        """
        Convert a file list to an asset collection.

        Returns:
            AssetCollection version of filelist
        """
        ac = AssetCollection()
        ac.assets = self.files
        return ac

    @staticmethod
    def from_asset_collection(asset_collection: AssetCollection) -> 'FileList':
        """
        Create a FileList from a AssetCollection.

        Args:
            asset_collection: AssetCollection to convert.

        Returns:
            FileList version of AssetCollection
        """
        fl = FileList()
        fl.files = [asset_collection.assets]
        return fl

    def __len__(self):
        """
        Length of FileList.

        Returns:
            Length
        """
        return len(self.files)

    def __iter__(self):
        """
        Iterator. Basically we proxy self.files.

        Returns:
            Iterator
        """
        return self.files.__iter__()

    def __getitem__(self, item):
        """
        Get file.

        Args:
            item: Item

        Returns:
            Item
        """
        return self.files.__getitem__(item)
