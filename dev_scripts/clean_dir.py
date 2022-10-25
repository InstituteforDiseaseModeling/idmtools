#!/usr/bin/env python
"""Utility script to allow downloading files using glob patterns for file, directories, etc, for any platform."""
import argparse
import os
import glob
import shutil
from contextlib import suppress


def clean_package_dir(glob_file_patterns, glob_delete_patterns, delete_directories):
    """
    Clean the repo using patterns specified.

    Args:
        glob_file_patterns: List of file patterns to remove
        glob_delete_patterns: List of directory patterns to delete
        delete_directories: List of directories to delete

    Returns:
        None
    """
    for gp in glob_file_patterns:
        for i in glob.glob(gp, recursive=True):
            with suppress(FileNotFoundError):
                os.remove(i)
    for gp in glob_delete_patterns:
        for i in glob.glob(gp, recursive=True):
            print(f"Removing directory: {i}")
            with suppress(FileNotFoundError):
                shutil.rmtree(i)
    for d in delete_directories:
        if os.path.exists(d):
            print(f"Removing directory: {d}")
            with suppress(FileNotFoundError):
                shutil.rmtree(d)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file-patterns', help='CSV separated list of glob patterns of files to delete')
    parser.add_argument('--dir-patterns', help='CSV separated list of glob patterns of directories to delete')
    parser.add_argument('--directories', help='CSV separated list of directories to delete')

    args = parser.parse_args()
    for a in ['file_patterns', 'dir_patterns', 'directories']:
        v = getattr(args, a).split(",") if isinstance(getattr(args, a), str) else []
        setattr(args, a, v)

    clean_package_dir(args.file_patterns, args.dir_patterns, args.directories)
