#!/usr/bin/env python3
"""
Extract structured review data from TikTok transcripts using OpenAI API.

This script processes transcripts and extracts:
- Review day number
- Foods reviewed with scores, categories and comments
- Flags posts that need manual review
"""

import json
import argparse
import os
from pathlib import Path
from typing import Optional, List, Dict
from collections import Counter
from openai import OpenAI


def create_extraction_prompt() -> str:
    """Create the system prompt for extracting review data."""
    return """You are a data extraction assistant. Your job is to read transcripts of school lunch reviews and extract structured information.

Extract the following information:
1. Review day number (if mentioned, e.g., "day 30 of reviewing school food")
2. List of all foods reviewed with their scores, comments and categories
3. Whether manual review is needed

Rules:
- Only extract from transcripts that mention "school food" or "school lunch"
- If no day number is mentioned, set it to null
- For each food item, extract:
  - Food name
  - Category (one of: main_dish, side, drink, dessert, condiment, snack, other)
  - Score (out of 10, as a number)
  - Comments (what was said about the food)
- If a score is given as a range (like "6.5-7"), use the first number
- Categorize foods appropriately:
  - main_dish: burgers, pizza, chicken nuggets, sandwiches, entrees
  - side: fries, tater tots, vegetables, salad, rice, breadsticks
  - drink: soda, juice, milk, water, sports drinks
  - dessert: cookies, cake, ice cream, pudding
  - condiment: ketchup, sauce, dressing
  - snack: chips, crackers, fruit
  - other: anything that doesn't fit the above

Flag for manual review if:
- Scores are unclear or ambiguous
- Food names are vague or uncertain
- Multiple scores given for same food without clarity
- Transcript is difficult to parse
- Missing expected information (e.g., mentions food but no score)
- Audio quality issues indicated by transcript (e.g., [inaudible])
- Unusual or unexpected content for a food review

Return data as JSON with this structure:
{
  "is_school_food_review": true/false,
  "day_number": number or null,
  "needs_review": true/false,
  "review_reason": "explanation why manual review is needed (or null if not needed)",
  "foods": [
    {
      "name": "food name",
      "category": "main_dish",
      "score": 7.5,
      "comments": "what was said about it"
    }
  ]
}

If the transcript does NOT mention school food or school lunch, return:
{
  "is_school_food_review": false,
  "day_number": null,
  "needs_review": false,
  "review_reason": null,
  "foods": []
}"""


def extract_review_data(transcript: str, client: OpenAI, model: str = "gpt-4o-mini") -> Dict:
    """
    Use OpenAI API to extract structured review data from a transcript.
    
    Args:
        transcript: The transcript text
        client: OpenAI client instance
        model: OpenAI model to use
        
    Returns:
        Dictionary with extracted review data
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": create_extraction_prompt()},
                {"role": "user", "content": f"Extract the review data from this transcript:\n\n{transcript}"}
            ],
            response_format={"type": "json_object"},
            temperature=0
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        print(f"  X OpenAI API error: {e}")
        return {
            "is_school_food_review": False,
            "day_number": None,
            "needs_review": False,
            "review_reason": None,
            "foods": [],
            "error": str(e)
        }


def process_transcripts(
    transcripts_json: str,
    api_key: Optional[str] = None,
    model: str = "gpt-4o-mini",
    update_mode: bool = False,
    existing_reviews_file: Optional[Path] = None
) -> Dict:
    """
    Process all transcripts and extract review data.
    
    Args:
        transcripts_json: Path to transcripts JSON file
        api_key: OpenAI API key (or use OPENAI_API_KEY env var)
        model: OpenAI model to use
        
    Returns:
        Dictionary with all extracted reviews
    """
    transcripts_path = Path(transcripts_json)
    
    if not transcripts_path.exists():
        raise FileNotFoundError(f"Transcripts file not found: {transcripts_json}")
    
    # Initialize OpenAI client
    if api_key is None:
        api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        raise ValueError("OpenAI API key required. Set OPENAI_API_KEY env var or use --api-key")
    
    client = OpenAI(api_key=api_key)
    
    # Load transcripts
    print(f"Loading transcripts from {transcripts_path}...")
    with open(transcripts_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    username = data.get('username', 'unknown')
    transcripts = data.get('transcripts', [])
    
    print(f"Found {len(transcripts)} transcripts for @{username}")
    print(f"Using model: {model}\n")
    
    # Load existing reviews if in update mode
    existing_reviews = []
    processed_post_ids = set()
    
    if update_mode and existing_reviews_file and existing_reviews_file.exists():
        print(f"\nUpdate mode: Loading existing reviews from {existing_reviews_file}...")
        try:
            with open(existing_reviews_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                existing_reviews = existing_data.get('reviews', [])
                processed_post_ids = {r['post_id'] for r in existing_reviews}
                print(f"  Found {len(existing_reviews)} existing reviews ({len(processed_post_ids)} post IDs)")
        except Exception as e:
            print(f"  Warning: Could not load existing reviews: {e}")
            print(f"  Proceeding with full processing...")
    
    results = {
        'username': username,
        'total_transcripts': len(transcripts),
        'school_food_reviews': 0,
        'other_content': 0,
        'failed': 0,
        'needs_manual_review': 0,
        'reviews': existing_reviews.copy(),  # Start with existing reviews
        'new_reviews_processed': 0,
        'skipped_existing': 0
    }
    
    # Process each transcript
    for i, transcript_data in enumerate(transcripts, 1):
        post_id = transcript_data.get('post_id', f'unknown_{i}')
        transcript_text = transcript_data.get('transcript', '')
        description = transcript_data.get('description', '')[:50]
        
        print(f"[{i}/{len(transcripts)}] Post {post_id}")
        print(f"  Description: {description}...")
        
        # Skip if already processed in update mode
        if update_mode and post_id in processed_post_ids:
            print(f"  Already processed, skipping...")
            results['skipped_existing'] += 1
            continue
        
        # Extract review data
        results['new_reviews_processed'] += 1
        review_data = extract_review_data(transcript_text, client, model)
        
        if 'error' in review_data:
            print(f"  X Failed to process")
            results['failed'] += 1
            continue
        
        # Check if this is a school food review
        if review_data.get('is_school_food_review', False):
            results['school_food_reviews'] += 1
            
            day_num = review_data.get('day_number')
            foods_count = len(review_data.get('foods', []))
            needs_review = review_data.get('needs_review', False)
            review_reason = review_data.get('review_reason')
            
            # Track manual review flags
            if needs_review:
                results['needs_manual_review'] += 1
            
            # Print status
            status = "OK"
            if needs_review:
                status = "WARNING"
            
            if day_num:
                print(f"  {status} School food review - Day {day_num}, {foods_count} foods")
            else:
                print(f"  {status} School food review - Day not mentioned, {foods_count} foods")
            
            if needs_review and review_reason:
                print(f"    WARNING: Needs review: {review_reason}")
            
            # Add to results
            results['reviews'].append({
                'post_id': post_id,
                'description': transcript_data.get('description', ''),
                'create_time': transcript_data.get('create_time', 0),
                'day_number': day_num,
                'needs_review': needs_review,
                'review_reason': review_reason,
                'foods': review_data.get('foods', []),
                'stats': transcript_data.get('stats', {})
            })
        else:
            results['other_content'] += 1
            print(f"  - Not a school food review, skipping")
    
    return results


def save_results(results: Dict, output_file: Path):
    """Save extracted review data to JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved review data to {output_file}")


def print_summary(results: Dict):
    """Print a summary of extracted reviews."""
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    # Show update mode stats if applicable
    if results.get('skipped_existing', 0) > 0:
        print(f"Update mode:")
        print(f"  Existing reviews: {len(results['reviews']) - results['school_food_reviews']}")
        print(f"  Skipped (already processed): {results['skipped_existing']}")
        print(f"  New reviews processed: {results['new_reviews_processed']}")
        print(f"  New school food reviews found: {results['school_food_reviews']}")
        print()
    
    print(f"Total transcripts: {results['total_transcripts']}")
    print(f"School food reviews: {results['school_food_reviews']} (from this run)")
    print(f"Total reviews in file: {len(results['reviews'])}")
    print(f"Other content: {results['other_content']}")
    print(f"Failed: {results['failed']}")
    print(f"Needs manual review: {results['needs_manual_review']}")
    
    if results['school_food_reviews'] > 0:
        reviews = results['reviews']
        
        # Count reviews with day numbers
        with_day = sum(1 for r in reviews if r['day_number'] is not None)
        print(f"\nReviews with day numbers: {with_day}")
        
        # Count total foods
        total_foods = sum(len(r['foods']) for r in reviews)
        avg_foods = total_foods / len(reviews) if reviews else 0
        print(f"Total foods reviewed: {total_foods}")
        print(f"Average foods per review: {avg_foods:.1f}")
        
        # Find highest and lowest scored foods
        all_foods = []
        for review in reviews:
            for food in review['foods']:
                if food.get('score') is not None:
                    all_foods.append(food)
        
        if all_foods:
            highest = max(all_foods, key=lambda x: x.get('score', 0))
            lowest = min(all_foods, key=lambda x: x.get('score', 10))
            
            print(f"\nHighest scored: {highest['name']} ({highest['score']}/10) - {highest.get('category', 'unknown')}")
            print(f"Lowest scored: {lowest['name']} ({lowest['score']}/10) - {lowest.get('category', 'unknown')}")
            
            # Category breakdown
            categories = Counter(f.get('category', 'unknown') for f in all_foods)
            print(f"\nFood categories:")
            for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                print(f"  {category}: {count}")
        
        # Show day range
        day_numbers = [r['day_number'] for r in reviews if r['day_number'] is not None]
        if day_numbers:
            print(f"\nDay range: Day {min(day_numbers)} to Day {max(day_numbers)}")


def main():
    """Command-line interface for the script."""
    parser = argparse.ArgumentParser(
        description="Extract structured review data from TikTok transcripts using OpenAI"
    )
    parser.add_argument(
        "transcripts_json",
        help="Path to transcripts JSON file (e.g., data/username/transcripts/username_transcripts.json)"
    )
    parser.add_argument(
        "--api-key",
        help="OpenAI API key (can also use OPENAI_API_KEY environment variable)"
    )
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="OpenAI model to use (default: gpt-4o-mini)"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: data/{username}/{username}_reviews.json)"
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update mode: only process new posts (skip already reviewed posts)"
    )
    
    args = parser.parse_args()
    
    try:
        # Determine output file first (needed for update mode)
        if args.output:
            output_file = Path(args.output)
        else:
            input_path = Path(args.transcripts_json)
            # Determine username from path for output file
            # Path is typically: data/username/transcripts/username_transcripts.json
            username_from_path = input_path.parent.parent.name
            output_file = input_path.parent.parent / f"{username_from_path}_reviews.json"
        
        # Process transcripts
        results = process_transcripts(
            args.transcripts_json,
            api_key=args.api_key,
            model=args.model,
            update_mode=args.update,
            existing_reviews_file=output_file if args.update else None
        )
        
        # Save results
        save_results(results, output_file)
        
        # Print summary
        print_summary(results)
        
        return 0
        
    except Exception as e:
        print(f"\nError: {e}")
        return 1


if __name__ == "__main__":
    exit(main())

