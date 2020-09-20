#!/usr/bin/env python
import glob
import os
from os.path import abspath, join, dirname, basename

base_directory = abspath(join(dirname(__file__), '..'))
dest_directory = join(base_directory, ".html_reports")
os.makedirs(dest_directory, exist_ok=True)
for file in glob.glob(join(base_directory, "**", "*.test_results.html"), recursive=True):
    dest_path = join(dest_directory, basename(file))
    if os.path.exists(dest_path):
        os.remove(dest_path)
    os.rename(file, dest_path)

asset_dest = join(dest_directory, "assets")
for file in glob.glob(join(base_directory, "**", "tests", "assets", "*"), recursive=True):
    dest_path = join(asset_dest, basename(file))
    if os.path.exists(dest_path):
        os.remove(dest_path)
    os.rename(file, dest_path)
