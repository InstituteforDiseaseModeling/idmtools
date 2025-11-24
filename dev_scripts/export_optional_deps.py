#!/usr/bin/env python3
"""
Export [project.optional-dependencies] from all pyproject.toml files
into corresponding requirements-*.txt files for Dependabot.
"""

import sys
import tomllib  # Python 3.11+
from pathlib import Path

root = Path(".", "..")
pyprojects = list(root.rglob("pyproject.toml"))

if not pyprojects:
    sys.exit(" No pyproject.toml files found.")

ALLOWED_GROUPS = {"dev", "build", "test"}
# Identify internal package name prefixes
INTERNAL_PREFIXES = ("idmtools_", "idmtools")

def is_internal_package(dep: str) -> bool:
    """
    Determine if a dependency looks like an internal idmtools package.
    """
    dep_name = dep.split("[")[0].split("==")[0].split(">=")[0].strip()
    return dep_name.startswith(INTERNAL_PREFIXES)

for pyfile in pyprojects:
    project_dir = pyfile.parent
    rel_dir = project_dir.relative_to(root)

    print(f" Processing {rel_dir}/pyproject.toml")

    with pyfile.open("rb") as f:
        data = tomllib.load(f)

    optional_deps = data.get("project", {}).get("optional-dependencies", {})
    if not optional_deps:
        print(f"  No optional dependencies found in {rel_dir}, skipping.")
        continue

    for group, deps in optional_deps.items():
        if group not in ALLOWED_GROUPS:
            continue
        external_deps = [d for d in deps if not is_internal_package(d)]
        if not external_deps:
            print(f"   Skipping {group} (contains only internal packages)")
            continue
        # Build filename prefix based on directory
        safe_dir = str(rel_dir).replace("/", "_").replace("\\", "_")
        if safe_dir == ".":
            safe_dir = "root"

        filename = f"requirements-{safe_dir}-{group}.txt"
        out_path = project_dir / filename
        with out_path.open("w", encoding="utf-8") as out:
            for dep in external_deps:
                out.write(f"{dep}\n")
        print(f"  Exported {len(external_deps)} {group} deps to {filename}")

print("\n All optional dependencies exported successfully.")
