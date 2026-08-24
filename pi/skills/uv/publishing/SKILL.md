---
name: uv-publishing
description: >
  Building and publishing Python packages with uv: building distributions,
  version management, publishing to PyPI, Trusted Publishing, custom indexes,
  and private packages.
---

# uv Publishing

Building and distributing Python packages with uv.

---

## Building Packages

```bash
uv build                           # Build sdist + wheel in current dir
uv build <SRC>                     # Build from specified dir
uv build --package <PACKAGE>       # Build specific workspace member
uv build --sdist                   # Source distribution only
uv build --wheel                   # Wheel only
uv build --no-sources              # Ignore tool.uv.sources (for publish verification)
```

Output goes to `dist/`.

---

## Version Management

```bash
uv version                          # Show current version
uv version 1.0.0                    # Set exact version
uv version --bump minor             # Bump minor (1.2.3 -> 1.3.0)
uv version --bump patch             # Bump patch
uv version --bump major             # Bump major
uv version --bump rc                # Bump release candidate
uv version --bump alpha             # Bump alpha
uv version --bump beta              # Bump beta
uv version --bump post              # Bump post release
uv version --bump dev               # Bump dev release
uv version --bump stable            # Clear pre-release
uv version --bump patch --bump dev  # Multi-component bump
uv version --dry-run 2.0.0          # Preview without writing
```

---

## Publishing

```bash
uv publish                         # Publish to PyPI (auto-detects credentials)
uv publish --token pypi-xxxxx      # Token authentication
uv publish --username __token__ --password pypi-xxxxx  # Username/password
uv publish --index testpypi        # Custom index (must have publish-url)
uv publish --check-url <url>       # Check for existing files before upload
```

### Authentication Methods (Priority Order)

1. `--token` / `UV_PUBLISH_TOKEN`
2. `--username` / `--password` or `UV_PUBLISH_USERNAME` / `UV_PUBLISH_PASSWORD`
3. **Trusted Publishing** (PyPI via GitHub Actions OIDC) — no credentials needed

### Custom Index Configuration

```toml
[[tool.uv.index]]
name = "testpypi"
url = "https://test.pypi.org/simple/"
publish-url = "https://test.pypi.org/legacy/"
explicit = true
```

---

## Trusted Publishing (GitHub Actions -> PyPI)

The recommended way to publish — no API tokens needed.

```yaml
name: Publish to PyPI
on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    environment: pypi           # GitHub environment with PyPI trust
    permissions:
      id-token: write           # Required for Trusted Publishing
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
      - run: uv python install 3.13
      - run: uv build
      - run: uv run --isolated --no-project --with dist/*.whl tests/smoke_test.py
      - run: uv publish
```

### PyPI Trusted Publisher Setup

1. Go to PyPI -> Your Project -> Publishing
2. Add a new trusted publisher:
   - Repository owner: `your-github-username`
   - Repository name: `your-repo`
   - Workflow: `publish.yml`
   - Environment: `pypi`

---

## Upload Attestations (PEP 740)

```bash
uv publish                         # Auto-discovers .publish.attestation files
uv publish --no-attestations       # Disable attestation uploads
```

---

## Marking Packages Private

```toml
[project]
classifiers = ["Private :: Do Not Upload"]
```

---

## Dynamic Versioning (from git tags)

Using `uv-dynamic-versioning`:

```toml
[build-system]
requires = ["hatchling", "uv-dynamic-versioning"]
build-backend = "hatchling.build"

[tool.hatch.version]
source = "uv-dynamic-versioning"

[tool.uv-dynamic-versioning]
vcs = "git"
style = "pep440"
```

Then version is automatically derived from git tags.

---

## Documentation

- **Publishing guide:** https://docs.astral.sh/uv/guides/package/
- **Build backend:** https://docs.astral.sh/uv/concepts/build-backend/
