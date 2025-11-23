"""
tiktools - A Python toolkit for TikTok data extraction and analysis.

This package provides tools for:
- Fetching TikTok post metadata
- Extracting transcripts from videos
- Analyzing TikTok content

Requires TikAPI key for core functionality.
"""

__version__ = "0.2.0"
__author__ = "Matt Stiles"
__license__ = "MIT"

from .api import TikAPIClient
from .posts import fetch_user_posts
from .transcripts import extract_transcripts, get_best_subtitle

__all__ = [
    "TikAPIClient",
    "fetch_user_posts",
    "extract_transcripts",
    "get_best_subtitle",
]

