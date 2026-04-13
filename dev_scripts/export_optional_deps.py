#!/usr/bin/env python3
"""
Export [project.optional-dependencies] from all pyproject.toml files into corresponding requirements-*.txt files for Dependabot.
"""

import sys
import tomllib  # Python 3.11+
from pathlib import Path

try:
    import tomli_w  # for writing TOML back
except ImportError:
    sys.exit("tomli_w is required to update pyproject.toml. Install with: pip install tomli-w")

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


def base_package_name(dep: str) -> str:
    """
    Extract the base package name from a dependency string, ignoring version specifiers and extras.
    Examples:
        'foo==1.2.3'     -> 'foo'
        'foo>=1.0'       -> 'foo'
        'foo[extra]==1'  -> 'foo'
    """
    # strip extras: foo[extra] -> foo
    name = dep.split("[")[0].strip()

    # strip common version operators
    for op in ("==", ">=", "<=", "~=", "!=", ">", "<"):
        if op in name:
            name = name.split(op)[0].strip()
            break
    return name


def parse_requirements_file(path: Path) -> dict[str, str]:
    """
    Read requirements-*.txt and return a mapping.
        base_name -> full_line
    Ignores blank lines and comments.
    """
    if not path.exists():
        return {}

    mapping: dict[str, str] = {}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            name = base_package_name(line)
            mapping[name] = line
    return mapping


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

    pyproject_modified = False  # track if we need to write pyproject.toml back
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

        # --- NEW BEHAVIOR: read existing requirements file and sync back to pyproject ---
        existing_reqs = parse_requirements_file(out_path)

        if existing_reqs:
            # Build a mapping from base_name -> current dep string in pyproject
            py_base_to_dep = {base_package_name(d): d for d in external_deps}

            for base_name, req_line in existing_reqs.items():
                if base_name not in py_base_to_dep:
                    # Requirement exists in file but not in pyproject[optional-deps][group]
                    # For now we ignore additions; you could also choose to add them.
                    continue

                current_dep = py_base_to_dep[base_name]
                if current_dep != req_line:
                    print(
                        f"   Detected version change for {base_name} in group '{group}': "
                        f"pyproject='{current_dep}' -> requirements='{req_line}'"
                    )
                    # Update the dependency in optional_deps[group]
                    idx = deps.index(current_dep)
                    deps[idx] = req_line
                    pyproject_modified = True

            # refresh external_deps after possible modifications
            external_deps = [d for d in deps if not is_internal_package(d)]

        with out_path.open("w", encoding="utf-8") as out:
            for dep in external_deps:
                out.write(f"{dep}\n")
        print(f"  Exported {len(external_deps)} {group} deps to {filename}")
    # If this pyproject.toml was modified, write it back
    if pyproject_modified:
        print(f"  Updating {rel_dir}/pyproject.toml with new optional-dependencies")
        data["project"]["optional-dependencies"] = optional_deps
        with pyfile.open("wb") as f:
            tomli_w.dump(data, f)

print("\n All optional dependencies exported successfully.")
