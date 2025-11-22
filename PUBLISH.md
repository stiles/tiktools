# Publishing tiktools to PyPI

This document describes the process for publishing tiktools to PyPI.

## Prerequisites

1. **Install build tools**:
   ```bash
   pip install build twine
   ```

2. **Set up PyPI API tokens**:
   - Get a PyPI API token from https://pypi.org/manage/account/token/
   - Get a TestPyPI token from https://test.pypi.org/manage/account/token/
   - Set environment variables:
     ```bash
     export PYPI="pypi-AgEIcGl..." # Your PyPI token
     export PYPI_TEST="pypi-AgEI..." # Your TestPyPI token
     ```
   - Or add to your `~/.zshrc` or `~/.bashrc`:
     ```bash
     export PYPI="pypi-AgEIcGl..."
     export PYPI_TEST="pypi-AgEI..."
     ```

## Pre-release checklist

Before running the publish script, make sure you have:

1. **Updated the version number** in both:
   - `pyproject.toml` (line 7)
   - `tiktools/__init__.py` (line 12)

2. **Updated CHANGELOG.md**:
   - Add a new section for the version
   - List all changes under Added, Changed, Fixed, etc.
   - Update the release date
   - Add a link to the GitHub release at the bottom

3. **Updated README.md**:
   - Verify all examples work
   - Update any changed API or features
   - Check that installation instructions are current

4. **Tested locally**:
   ```bash
   # Install in development mode
   pip install -e .
   
   # Test the CLI scripts
   python scripts/fetch_posts.py --help
   python scripts/extract_transcripts.py --help
   
   # Run any tests
   pytest tests/
   ```

5. **Committed and pushed all changes**:
   ```bash
   git add .
   git commit -m "Bump version to X.Y.Z"
   git push origin main
   ```

## Publishing process

### Step 1: Test on TestPyPI (recommended)

Run the publish script and select TestPyPI:

```bash
./scripts/publish.sh
```

When prompted:
1. Confirm all pre-flight checks
2. Select "Publish to TestPyPI"

Test the installation:
```bash
pip install -i https://test.pypi.org/simple/ tiktools==X.Y.Z
```

### Step 2: Publish to PyPI

Once you've verified the TestPyPI version works, run the script again:

```bash
./scripts/publish.sh
```

When prompted:
1. Confirm all pre-flight checks
2. Select "Publish to PyPI (Official)"
3. Confirm the final prompt

### Step 3: Create GitHub release

After publishing to PyPI:

1. Go to https://github.com/stiles/tiktools/releases/new
2. Create a new tag: `vX.Y.Z` (e.g., `v0.1.0`)
3. Release title: `tiktools X.Y.Z`
4. Copy the CHANGELOG.md section for this version into the release notes
5. Publish the release

## Non-interactive mode (CI/CD)

For automated publishing in CI/CD:

```bash
# Publish to TestPyPI
NONINTERACTIVE=1 PUBLISH_TARGET="Publish to TestPyPI" ./scripts/publish.sh

# Publish to PyPI
NONINTERACTIVE=1 PUBLISH_TARGET="Publish to PyPI (Official)" ./scripts/publish.sh
```

## Troubleshooting

### Error: "A file already exists"

This means the version has already been published to PyPI. You cannot overwrite existing versions. You must:
1. Bump the version number
2. Update CHANGELOG.md
3. Commit and try again

### Error: "Invalid token"

Your PyPI token is incorrect or expired. Generate a new token from:
- PyPI: https://pypi.org/manage/account/token/
- TestPyPI: https://test.pypi.org/manage/account/token/

### Build fails

Make sure you have the build tools installed:
```bash
pip install --upgrade build twine
```

## Versioning scheme

tiktools follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version (X.0.0): Incompatible API changes
- **MINOR** version (0.X.0): New functionality, backwards compatible
- **PATCH** version (0.0.X): Bug fixes, backwards compatible

Example progression:
- `0.1.0` - Initial release
- `0.1.1` - Bug fix
- `0.2.0` - New feature (backwards compatible)
- `1.0.0` - First stable release or breaking changes

## Post-release

After publishing:

1. Announce on social media / relevant channels
2. Update any documentation sites
3. Close any GitHub issues fixed by this release
4. Start planning the next version

