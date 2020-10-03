#!/usr/bin/env python

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
webbrowser.open(arg)
