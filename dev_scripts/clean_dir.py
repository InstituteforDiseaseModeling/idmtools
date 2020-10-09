#!/usr/bin/env python
import argparse
import os
import glob
import shutil


def clean_package_dir(glob_file_patterns, glob_delete_patterns, delete_directories):
    for gp in glob_file_patterns:
        for i in glob.glob(gp, recursive=True):
            print(f"Removing {i}")
            try:
                os.remove(i)
            except FileNotFoundError:
                pass
    for gp in glob_delete_patterns:
        for i in glob.glob(gp, recursive=True):
            print(f"Removing directory: {i}")
            try:
                shutil.rmtree(i)
            except FileNotFoundError:
                pass
    for d in delete_directories:
        if os.path.exists(d):
            print(f"Removing directory: {d}")
            try:
                shutil.rmtree(d)
            except FileNotFoundError:
                pass


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
