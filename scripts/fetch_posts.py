#!/usr/bin/env python3
"""
CLI tool to fetch TikTok post metadata.

Usage:
    python fetch_posts.py USERNAME [options]
    
Example:
    python fetch_posts.py davis_big_dawg --update
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path so we can import tiktools
sys.path.insert(0, str(Path(__file__).parent.parent))

from tiktools import fetch_user_posts


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Fetch TikTok user post metadata"
    )
    parser.add_argument(
        "username",
        help="TikTok username (without @)"
    )
    parser.add_argument(
        "--api-key",
        help="TikAPI API key (or use TIKAPI_KEY environment variable)"
    )
    parser.add_argument(
        "--max-posts",
        type=int,
        help="Maximum number of posts to retrieve (default: all)"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output JSON file path (default: data/{username}/{username}_posts.json)"
    )
    parser.add_argument(
        "--sandbox",
        action="store_true",
        help="Use sandbox server for testing"
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update mode: only fetch new posts"
    )
    parser.add_argument(
        "--download-thumbnails",
        action="store_true",
        help="Download thumbnails immediately (recommended - URLs expire quickly)"
    )
    parser.add_argument(
        "--thumbnail-type",
        choices=["cover", "origin", "dynamic", "zoom_240", "zoom_480", "zoom_720", "zoom_960"],
        default="cover",
        help="Type of thumbnail to download (default: cover)"
    )
    
    args = parser.parse_args()
    
    # Determine output file
    output_file = args.output
    if output_file is None:
        output_dir = Path("data") / args.username
        output_file = output_dir / f"{args.username}_posts.json"
    
    try:
        fetch_user_posts(
            username=args.username,
            api_key=args.api_key,
            max_posts=args.max_posts,
            output_file=output_file,
            sandbox=args.sandbox,
            update_mode=args.update,
            download_thumbnails=args.download_thumbnails,
            thumbnail_type=args.thumbnail_type
        )
        return 0
    except Exception as e:
        print(f"\nError: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

