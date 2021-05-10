#!/usr/bin/env python
"""This script aggregates code coverage reports into '<repo>/.html_reports'."""  # noqa: 212
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
