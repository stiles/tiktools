#!/usr/bin/env python3
"""
Generic analysis template.

This is a starter template for building custom analysis tools.
See examples/food_reviews/ for a complete working example.

Usage:
    python analyze.py TRANSCRIPTS_FILE [options]
"""

import argparse
import json
import sys
from pathlib import Path


def analyze_transcripts(transcripts_file: Path):
    """
    Analyze transcripts - customize this function for your needs.
    
    Args:
        transcripts_file: Path to transcripts JSON file
    """
    print(f"Loading transcripts from {transcripts_file}...")
    
    with open(transcripts_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    username = data.get('username', 'unknown')
    transcripts = data.get('transcripts', [])
    
    print(f"Found {len(transcripts)} transcripts for @{username}")
    
    # TODO: Add your custom analysis logic here
    # For a complete example, see examples/food_reviews/extract_reviews.py
    
    # Example: Count transcripts with original audio
    original_audio_count = sum(
        1 for t in transcripts 
        if t.get('is_original_audio', False)
    )
    
    print(f"\nBasic statistics:")
    print(f"  Total transcripts: {len(transcripts)}")
    print(f"  Original audio: {original_audio_count}")
    print(f"  Non-original audio: {len(transcripts) - original_audio_count}")
    
    # Example: Average transcript length
    if transcripts:
        avg_length = sum(len(t['transcript']) for t in transcripts) / len(transcripts)
        print(f"  Average transcript length: {avg_length:.0f} characters")


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Analyze TikTok transcripts (generic template)"
    )
    parser.add_argument(
        "transcripts_file",
        type=Path,
        help="Path to transcripts JSON file"
    )
    
    args = parser.parse_args()
    
    if not args.transcripts_file.exists():
        print(f"Error: File not found: {args.transcripts_file}")
        return 1
    
    try:
        analyze_transcripts(args.transcripts_file)
        return 0
    except Exception as e:
        print(f"\nError: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

