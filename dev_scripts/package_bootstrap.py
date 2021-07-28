#!/usr/bin/env python
"""Convenience script to run install for packing environment."""
import subprocess
from os.path import abspath, dirname

base_directory = abspath(dirname(__file__))
subprocess.run(["pip", "install", "-r", "package_requirements.txt"], cwd=base_directory)
