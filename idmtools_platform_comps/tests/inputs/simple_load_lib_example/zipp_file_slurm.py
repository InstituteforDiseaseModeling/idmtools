# -*- coding: utf-8 -*-
import io
import os
import sys
import zipfile
CURRENT_DIRECTORY = os.path.dirname(__file__)
LIBRARY_PATH = os.path.join(CURRENT_DIRECTORY, 'site_packages')  # Need to site_packages level!!!

sys.path.insert(0, LIBRARY_PATH)  # Very Important!
import zipp

consume = tuple

def add_dirs(zf):
    """
    Given a writable zip file zf, inject directory entries for
    any directories implied by the presence of children.
    """
    for name in zipp.CompleteDirs._implied_dirs(zf.namelist()):
        zf.writestr(name, b"")
    return zf

def build_alpharep_fixture():
    data = io.BytesIO()
    zf = zipfile.ZipFile(data, "w")
    zf.writestr("a.txt", b"content of a")
    zf.writestr("b/c.txt", b"content of c")
    zf.writestr("b/d/e.txt", b"content of e")
    zf.writestr("b/f.txt", b"content of f")
    zf.writestr("g/h/i.txt", b"content of i")
    zf.filename = "alpharep.zip"
    return zf

if __name__ == "__main__":
    zf = build_alpharep_fixture()
    for name in zipp.CompleteDirs._implied_dirs(zf.namelist()):
        print(name)
