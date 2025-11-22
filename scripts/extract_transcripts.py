#!/usr/bin/env python3
"""
CLI tool to extract transcripts from TikTok posts.

Usage:
    python extract_transcripts.py POSTS_FILE [options]
    
Example:
    python extract_transcripts.py data/user/user_posts.json --update
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path so we can import tiktools
sys.path.insert(0, str(Path(__file__).parent.parent))

from tiktools import extract_transcripts


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Extract transcripts from TikTok posts using subtitle files"
    )
    parser.add_argument(
        "posts_file",
        type=Path,
        help="Path to posts JSON file"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory to save transcripts (default: same dir as posts_file/transcripts)"
    )
    parser.add_argument(
        "--format",
        choices=["individual", "combined", "both"],
        default="individual",
        help="Output format (default: individual)"
    )
    parser.add_argument(
        "--language",
        default="eng",
        help="Preferred language code for subtitles (default: eng)"
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update mode: only process new posts"
    )
    
    args = parser.parse_args()
    
    try:
        results = extract_transcripts(
            posts_file=args.posts_file,
            output_dir=args.output_dir,
            output_format=args.format,
            language=args.language,
            update_mode=args.update
        )
        
        # Print summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        
        if results.get('skipped_existing', 0) > 0:
            print(f"Update mode:")
            print(f"  Existing transcripts: {results.get('skipped_existing', 0)}")
            print(f"  New transcripts: {results['transcripts_downloaded']}")
            print(f"  Total transcripts: {len(results['transcripts'])}")
            print()
        
        print(f"Total posts: {results['total_posts']}")
        print(f"Transcripts found: {results['transcripts_found']}")
        print(f"Transcripts downloaded: {results['transcripts_downloaded']}")
        print(f"Failed: {results['failed']}")
        
        if results['transcripts_downloaded'] > 0:
            total_chars = sum(len(t['transcript']) for t in results['transcripts'])
            avg_chars = total_chars / len(results['transcripts'])
            print(f"\nTotal characters: {total_chars:,}")
            print(f"Average per transcript: {avg_chars:.0f} characters")
        
        return 0
        
    except Exception as e:
        print(f"\nError: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

