# Release process

This page describes how to manage versioning, build and publish Python packages to PyPI, build and publish Docker images, and deploy documentation — all through GitHub Actions.

---

## Overview

The release pipeline consists of the following coordinated steps:

```
0. Update changelog (docs/changelog.md)
        ↓
1. Create a git tag (vX.Y.Z)
        ↓
2. Build & publish packages to PyPI
        ↓
3. Build & publish Docker images
        ↓
4. Deploy documentation
```

All workflows are defined in `.github/workflows/`.

---

## 0. Updating the changelog

Before cutting a release tag, update `docs/changelog.md` with all issues from the associated GitHub project.

### Prerequisites

- [GitHub CLI (`gh`)](https://cli.github.com/) installed.
- Authenticated via `gh auth login`.
- Python dependencies installed (`pandas`).

### Steps

1. Identify the GitHub project number for the release. For example, project **83** tracks the `3.1.0` milestone.  
   Find it in the project URL: `https://github.com/orgs/InstituteforDiseaseModeling/projects/<number>`.

2. Run the script from the `dev_scripts/` directory:

    ```bash
    cd dev_scripts
    python project_changelog.py --project_id 83 --version 3.1.0
    ```

3. Review the updated `docs/changelog.md` to verify entries look correct, then commit:

    ```bash
    git add docs/changelog.md
    git commit -m "Update changelog for X.Y.Z release"
    ```

---

## 1. Versioning

### How versions work

All packages use [`setuptools-scm`](https://setuptools-scm.readthedocs.io/) for **fully dynamic versioning**. There is no static version stored in any `pyproject.toml` — every package declares `dynamic = ["version"]` and the version is computed at build time directly from the git tag:

```toml
[project]
dynamic = ["version"]

[tool.setuptools_scm]
root = ".."
version_scheme = "no-guess-dev"
local_scheme = "no-local-version"
fallback_version = "0.0.0.dev0"
```

- **Tag format**: `v{MAJOR}.{MINOR}.{PATCH}` (e.g., `v3.0.6`)
- **Fallback** (no tag reachable): `0.0.0.dev0`
- **`no-local-version`**: strips the `+gHASH` local suffix so published wheels have clean version strings

### Version between tags

We only update tags with releases. Between releases, `setuptools-scm` automatically appends a post-release and dev segment to reflect the number of commits since the last tag:

```
{last_tag}.post1.dev{commit_distance}
```

For example, 4 commits after tagging `v3.0.6`:

```
idmtools:                  3.0.6.post1.dev4
idmtools_cli:              3.0.6.post1.dev4
idmtools_platform_comps:   3.0.6.post1.dev5
idmtools_models:           3.0.6.post1.dev5
idmtools_platform_general: 3.0.6.post1.dev5
idmtools_platform_slurm:   3.0.6.post1.dev6
idmtools_platform_container: 3.0.6.post1.dev5
idmtools_test:             3.0.6.post1.dev5
```

The `dev` number varies per package because each package's version is computed independently based on how many commits have touched files under its subdirectory since the last tag.

You can check the current version of all installed packages at any time:

```bash
python dev_scripts/get_version.py
```

The built wheel filename and package metadata reflect whatever `setuptools-scm` resolves at `python -m build` time. No file editing is needed to change the version; **creating a new git tag is the only required action**.

### Creating a new version

To release a new version, create and push an annotated git tag. That is the only step required — `setuptools-scm` picks it up automatically at build time.

```bash
git tag v3.1.0
git push origin v3.1.0
```

Pushing a `v*` tag triggers the **Deploy Packages** workflow, which builds all packages and publishes them to PyPI (after manual approval).

!!! tip "How the version flows into built packages"
    When `python -m build` runs, `setuptools-scm` walks the git history, finds the nearest `v*` tag, and injects that value as the package version. No file editing is needed.

---

## 2. Building and publishing Python packages

### Packages in this repository

The monorepo contains 8 packages, all built in parallel:

| Package directory | PyPI name |
|---|---|
| `idmtools_core` | `idmtools` |
| `idmtools_cli` | `idmtools-cli` |
| `idmtools_models` | `idmtools-models` |
| `idmtools_platform_comps` | `idmtools-platform-comps` |
| `idmtools_platform_general` | `idmtools-platform-general` |
| `idmtools_platform_slurm` | `idmtools-platform-slurm` |
| `idmtools_platform_container` | `idmtools-platform-container` |
| `idmtools_test` | `idmtools-test` |

### Workflow: Deploy Packages (`deploy.yml`)

**Triggers**:

| Event | What happens                                                                |
|---|-----------------------------------------------------------------------------|
| Push to `main` branch | Builds packages only (no upload)                                            |
| Tag matching `v*` | Builds packages → publishes to PyPI (after approval) → builds Docker images |
| Manual dispatch with `target=test` | Builds + publishes to TestPyPI + builds Docker staging image                |



Each step is explained below. No manual intervention is required beyond the trigger events mentioned above.

### Step 1 — Build all packages

Each package is built using the PEP 517 build frontend:

```bash
cd idmtools_{package}
python -m build
```

This produces both a source distribution (`.tar.gz`) and a wheel (`.whl`) in `idmtools_{package}/dist/`. Built artifacts are uploaded as GitHub Actions artifacts with a 1-day retention.

### Step 2 — Publish to TestPyPI (manual, optional)

Run the **Deploy Packages** workflow manually from with `target=test`:

1. Go to **Actions → Deploy Packages**.
2. Click **Run workflow**, select a branch you want to build from, set **Where to upload** to `test`.
3. Packages are uploaded to [TestPyPI](https://test.pypi.org/) using the `TEST_PYPI_API_TOKEN` secret.
4. `skip-existing: true` prevents errors if the version already exists.

Install from TestPyPI to verify:

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ idmtools==3.x.x
```

### Step 3 — Publish to production PyPI (automatic on tag)

When a `v*` tag is pushed (created by the `git tag`):

1. All 8 packages are built.
2. The `publish-to-pypi` job waits for a manual approval from reviewers in the `deploy_pypi` GitHub environment.
3. After approval, packages are published using [OIDC Trusted Publishers](https://docs.pypi.org/trusted-publishers/) — no API token needed.

!!! warning "Manual approval required"
    Production PyPI publishing requires a reviewer to approve the `deploy_pypi` environment gate in the GitHub Actions UI before the upload proceeds.

### Local build and staging upload

```bash
# Build all packages locally
make dist

# Upload to test pypi
twine upload dist/* --repository-url https://test.pypi.org/legacy/
```

---

## 3. Building and publishing Docker images

Two Docker images are maintained in this repository, both published to the [GitHub Container Registry (GHCR)](https://ghcr.io/institutefordiseasemodeling/).

### Image 1 — SSMT worker image (COMPS platform)

**Registry path**: `ghcr.io/institutefordiseasemodeling/idmtools_comps_ssmt_worker`

**Build script**: `idmtools_platform_comps/ssmt_image/build_ssmt_image.py`

#### Staging image

**Trigger**: Manual dispatch via **Deploy Packages** with `target=test`, or via the separate **Build SSMT Image Staging** workflow (`build_ssmt_image_staging.yml`).

```
Actions → Build SSMT Image Staging → Run workflow
```

The workflow:

1. Installs `idmtools_platform_comps` from the build artifacts.
2. Logs into GHCR using `GITHUB_TOKEN`.
3. Runs the build script to build and push a staging image:

```bash
cd idmtools_platform_comps/ssmt_image
python build_ssmt_image.py --push
```

#### Production image

**Trigger**: Automatically after a `v*` tag is pushed and all packages are published to PyPI.

```bash
python build_ssmt_image.py --production --push
```

The build script:

- Queries GHCR to determine the next build number automatically.
- Tags the image with three tags:
    - Full version: `3.1.0.5`
    - Base version: `3.1.0`
    - `latest`

#### Local build (without push)

```bash
cd idmtools_platform_comps/ssmt_image
make docker-build
```

To build and push manually:

```bash
make docker-build-publish-staging   # staging
make docker-build-publish           # production
```

---

### Image 2 — Container platform runtime image

**Registry path**: `ghcr.io/institutefordiseasemodeling/container-rocky-runtime`

**Build script**: `idmtools_platform_container/docker_image/build_container_image.py`

**Trigger**: Manual dispatch only via the **Build Container Image** workflow (`build_container_image.yml`).

```
Actions → Build Container Image → Run workflow
```

The workflow runs:

```bash
cd idmtools_platform_container/docker_image
python build_container_image.py --push
```

The script:

- Reads `BASE_VERSION` file for the base version string.
- Queries GHCR to calculate the next build number automatically.
- Builds using the `Dockerfile` in the same directory.
- Tags and pushes to GHCR.

To build without pushing:

```bash
python build_container_image.py
```

---

### GHCR authentication (local builds)

```bash
echo YOUR_GITHUB_PAT | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

The token requires `write:packages` and `read:packages` scopes.

---

## 4. Building and deploying documentation

Documentation is built with [MkDocs](https://www.mkdocs.org/) and the [Material theme](https://squidfunk.github.io/mkdocs-material/), then deployed to GitHub Pages.

**Live site**: `https://institutefordiseasemodeling.github.io/idmtools/`

### Workflow: Deploy MkDocs (`deploy_docs_api.yml`)

**Triggers**:

| Event | What happens |
|---|---|
| Push to `main` branch | Builds and deploys docs automatically |
| Manual dispatch | Builds and deploys on demand |

### Building docs locally

```bash
# Install documentation dependencies
pip install -r docs/requirements.txt

# Build once
mkdocs build

# Serve locally with auto-reload at http://localhost:8000
mkdocs serve
```

!!! note "Concurrency protection"
    The workflow uses a `pages` concurrency group with `cancel-in-progress: false` to prevent partial deployments from being cancelled.

### Documentation dependencies

From `docs/requirements.txt`:

```
mkdocs>=1.6.0
mkdocs-material>=9.5.0
pymdown-extensions>=10.7.0
mkdocs-minify-plugin>=0.8.0
```

---

## 5. Full release checklist

Use this checklist when cutting a new release:

- [ ] All changes merged to `dev` branch and tests passing.
- [ ] Create new release tag with `git tag vx.y.z` and push to repo with `git push origin vx.y.z`  
- [ ] Verify the new tag (e.g., `v3.1.0`) appears in the repository.
- [ ] Merge `dev` → `main` via pull request.
- [ ] The push to `main` triggers:
    - [ ] **Deploy Packages** — builds all 8 packages.
    - [ ] **Deploy MkDocs** — builds and deploys documentation to GitHub Pages.
- [ ] To publish to **TestPyPI** (optional validation step before release):
    - Run **Actions → Deploy Packages** manually on `any branch` with `target=test`.
    - Install from TestPyPI and smoke-test.
- [ ] Once confident, the `v*` tag triggers **production PyPI publish** — approve the `deploy_pypi` environment gate when prompted.
- [ ] After PyPI publish succeeds, the **SSMT Docker image** is automatically built and pushed to GHCR.
- [ ] To rebuild the **Container Runtime image** separately: run **Actions → Build Container Image** manually.

---

## 6. Required secrets and environments

| Secret / environment | Used by | Purpose |
|---|---|---|
| `TEST_PYPI_API_TOKEN` | `deploy.yml` | Upload to TestPyPI |
| `GITHUB_TOKEN` | `deploy.yml`, `deploy_docs_api.yml`, `build_ssmt_image_staging.yml` | GHCR login, Pages deploy (auto-provided by GitHub) |
| `deploy_pypi` environment | `deploy.yml` | Manual approval gate for production PyPI publish |

