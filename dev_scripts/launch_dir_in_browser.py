#!/usr/bin/env python
"""Launches a directory in a browser.

This script is used to view local documentation, coverage reports, etc
"""
import os
import sys
import webbrowser

try:
    from urllib import pathname2url
except:  # noqa E722
    from urllib.request import pathname2url

arg = sys.argv[1]
if not arg.startswith("http"):
    arg = "file://" + pathname2url(os.path.abspath(arg))
print(f"Launching {arg}")
webbrowser.open(arg)
