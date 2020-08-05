import io
import os
import sys
import zipfile
CURRENT_DIRECTORY = os.path.dirname(__file__)
LIBRARY_PATH = os.path.join(CURRENT_DIRECTORY, 'site-packages')  # Need to site-packages level!!!

sys.path.insert(0, LIBRARY_PATH)  # Very Important!
import zipp  # noqa

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
    """
    Create a zip file with this structure:
    .
    ├── a.txt
    ├── b
    │   ├── c.txt
    │   ├── d
    │   │   └── e.txt
    │   └── f.txt
    └── g
        └── h
            └── i.txt
    This fixture has the following key characteristics:
    - a file at the root (a)
    - a file two levels deep (b/d/e)
    - multiple files in a directory (b/c, b/f)
    - a directory containing only a directory (g/h)
    "alpha" because it uses alphabet
    "rep" because it's a representative example
    """
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
