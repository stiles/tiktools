"""Integration tests for tiktools package."""

import pytest
from pathlib import Path
from tiktools import __version__, TikAPIClient, fetch_user_posts, extract_transcripts, get_best_subtitle


class TestPackageImports:
    """Test that package imports work correctly."""
    
    def test_version_exists(self):
        """Test that version is defined."""
        assert __version__ is not None
        assert isinstance(__version__, str)
    
    def test_main_exports(self):
        """Test that main functions are exported."""
        assert TikAPIClient is not None
        assert fetch_user_posts is not None
        assert extract_transcripts is not None
        assert get_best_subtitle is not None


class TestVersionConsistency:
    """Test that version is consistent across files."""
    
    def test_version_matches_pyproject(self):
        """Test that __version__ matches pyproject.toml."""
        import re
        from tiktools import __version__
        
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with open(pyproject_path, 'r') as f:
            content = f.read()
        
        match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.M)
        assert match is not None, "Could not find version in pyproject.toml"
        
        pyproject_version = match.group(1)
        assert __version__ == pyproject_version, \
            f"Version mismatch: __init__.py has {__version__}, pyproject.toml has {pyproject_version}"

