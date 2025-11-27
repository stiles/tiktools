#!/usr/bin/env python3
"""
CLI tool to download thumbnails from TikTok posts.

Usage:
    python download_thumbnails.py POSTS_FILE [options]
    
Example:
    python download_thumbnails.py data/user/user_posts.json --type origin --update
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path so we can import tiktools
sys.path.insert(0, str(Path(__file__).parent.parent))

from tiktools import download_thumbnails


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Download thumbnails from TikTok posts"
    )
    parser.add_argument(
        "posts_file",
        type=Path,
        help="Path to posts JSON file"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory to save thumbnails (default: same dir as posts_file/thumbnails)"
    )
    parser.add_argument(
        "--type",
        choices=["cover", "origin", "dynamic", "zoom_240", "zoom_480", "zoom_720", "zoom_960"],
        default="cover",
        help="Type of thumbnail to download (default: cover)"
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update mode: only download thumbnails for new posts"
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip posts that already have thumbnail files (protects manual organization)"
    )
    
    args = parser.parse_args()
    
    try:
        results = download_thumbnails(
            posts_file=args.posts_file,
            output_dir=args.output_dir,
            thumbnail_type=args.type,
            update_mode=args.update,
            skip_existing=args.skip_existing
        )
        
        # Print summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        
        if results.get('skipped_existing', 0) > 0:
            if args.update:
                print(f"Update mode:")
            elif args.skip_existing:
                print(f"Skip-existing mode:")
            print(f"  Existing thumbnails: {results.get('skipped_existing', 0)}")
            print(f"  New thumbnails: {results['thumbnails_downloaded']}")
            print(f"  Total thumbnails: {len(results['thumbnails'])}")
            print()
        
        print(f"Total posts: {results['total_posts']}")
        print(f"Thumbnails found: {results['thumbnails_found']}")
        print(f"Thumbnails downloaded: {results['thumbnails_downloaded']}")
        print(f"Failed: {results['failed']}")
        
        if results['thumbnails_downloaded'] > 0:
            total_size = sum(t['file_size'] for t in results['thumbnails'])
            avg_size = total_size / len(results['thumbnails'])
            print(f"\nTotal size: {total_size / 1024 / 1024:.2f} MB")
            print(f"Average per thumbnail: {avg_size / 1024:.1f} KB")
        
        return 0
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

