#!/usr/bin/env python

# This script should be executed from the root directory of the repo
import argparse
import os
from livereload import Server, shell


parser = argparse.ArgumentParser("Serves and autobuilds the docs")
parser.add_argument('--port', type=int, default=8000, help="Port to serve docs on.")
args = parser.parse_args()

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(root_dir)
server = Server()
server.watch('docs/*.rst', shell('make html', cwd='docs'), delay=5, ignore=lambda x: "idmtools_" in x)
server.watch('docs/__static/*', shell('make html', cwd='docs'), delay=5)
server.watch('docs/diagrams/*', shell('make html', cwd='docs'), delay=5)
server.watch('docs/images/*', shell('make html', cwd='docs'), delay=5)
server.watch('docs/*.txt', shell('make html', cwd='docs'), delay=5)
server.watch('docs/*.py', shell('make html', cwd='docs'), delay=5)
server.serve(root='docs/_build/html', port=args.port)
