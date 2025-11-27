#!/usr/bin/env python3
"""
CLI tool to translate TikTok transcripts.

Usage:
    python translate_transcripts.py TRANSCRIPTS_FILE --target LANG [options]
    
Example:
    python translate_transcripts.py data/user/transcripts/user_transcripts.json --target en es
    python translate_transcripts.py data/user/transcripts/user_transcripts.json --target en --estimate-only
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path so we can import tiktools
sys.path.insert(0, str(Path(__file__).parent.parent))

from tiktools import translate_transcripts


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Translate TikTok transcripts using cloud translation services"
    )
    parser.add_argument(
        "transcripts_file",
        type=Path,
        help="Path to transcripts JSON file"
    )
    parser.add_argument(
        "--target",
        nargs="+",
        required=True,
        help="Target language code(s) (e.g., en es fr)"
    )
    parser.add_argument(
        "--service",
        choices=["aws"],
        default="aws",
        help="Translation service to use (default: aws)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory to save translations (default: same dir as transcripts_file)"
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update mode: only translate new transcripts"
    )
    parser.add_argument(
        "--estimate-only",
        action="store_true",
        help="Only estimate translation costs without translating"
    )
    parser.add_argument(
        "--source-language",
        help="Source language code (auto-detected if not specified)"
    )
    
    args = parser.parse_args()
    
    try:
        results = translate_transcripts(
            transcripts_file=args.transcripts_file,
            target_languages=args.target,
            service=args.service,
            output_dir=args.output_dir,
            update_mode=args.update,
            estimate_only=args.estimate_only,
            source_language=args.source_language
        )
        
        # Print summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        
        if args.estimate_only:
            print("COST ESTIMATE")
            print(f"Total characters: {results['total_characters']:,}")
            print(f"Target languages: {len(args.target)}")
            print(f"Estimated cost: ${results['estimated_cost']:.4f} USD")
            print("\nTo proceed with translation, run without --estimate-only")
            return 0
        
        if results.get('skipped_existing', 0) > 0:
            print(f"Update mode:")
            print(f"  Existing translations: {results.get('skipped_existing', 0)}")
            print(f"  New translations: {results['translations_created']}")
            print()
        
        print(f"Total transcripts: {results['total_transcripts']}")
        print(f"Translations created: {results['translations_created']}")
        print(f"  Service translated: {results['service_translated']}")
        print(f"  TikTok subtitles used: {results['tiktok_subtitles_used']}")
        print(f"Failed: {results['failed']}")
        
        if results['estimated_cost'] > 0:
            print(f"\nEstimated cost: ${results['estimated_cost']:.4f} USD")
        
        if results['translations_created'] > 0:
            total_chars = sum(t['character_count'] for t in results['translations'])
            avg_chars = total_chars / len(results['translations'])
            print(f"\nTotal characters translated: {total_chars:,}")
            print(f"Average per translation: {avg_chars:.0f} characters")
        
        return 0
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

