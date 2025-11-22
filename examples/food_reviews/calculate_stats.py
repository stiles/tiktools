#!/usr/bin/env python3
"""
Calculate summary statistics from TikTok review data.

This script reads a reviews JSON file and calculates statistics like:
- Overall average scores
- Category averages
- Daily averages
- Trends over time

No API calls required - can be run anytime on existing data.
"""

import json
import argparse
from pathlib import Path
from typing import Dict
from collections import Counter


def calculate_summary_stats(reviews: list) -> Dict:
    """
    Calculate summary statistics for reviews.
    
    Args:
        reviews: List of review dictionaries
        
    Returns:
        Dictionary with summary statistics
    """
    if not reviews:
        return {}
    
    # Calculate average score by day
    day_scores = {}
    for review in reviews:
        day_num = review.get('day_number')
        if day_num is not None:
            foods = review.get('foods', [])
            scores = [f.get('score') for f in foods if f.get('score') is not None]
            if scores:
                avg_score = sum(scores) / len(scores)
                if day_num not in day_scores:
                    day_scores[day_num] = []
                day_scores[day_num].append(avg_score)
    
    # Average the scores for each day (in case multiple reviews per day)
    daily_averages = {
        day: round(sum(scores) / len(scores), 2)
        for day, scores in day_scores.items()
    }
    
    # Calculate average score by category across all reviews
    category_scores = {}
    for review in reviews:
        for food in review.get('foods', []):
            category = food.get('category', 'unknown')
            score = food.get('score')
            if score is not None:
                if category not in category_scores:
                    category_scores[category] = []
                category_scores[category].append(score)
    
    category_averages = {
        category: {
            'average_score': round(sum(scores) / len(scores), 2),
            'count': len(scores),
            'min_score': min(scores),
            'max_score': max(scores)
        }
        for category, scores in category_scores.items()
    }
    
    # Overall statistics
    all_scores = []
    for category_data in category_scores.values():
        all_scores.extend(category_data)
    
    overall_stats = {}
    if all_scores:
        overall_stats = {
            'average_score': round(sum(all_scores) / len(all_scores), 2),
            'total_items_scored': len(all_scores),
            'min_score': min(all_scores),
            'max_score': max(all_scores)
        }
    
    # Food item statistics
    food_names = {}
    for review in reviews:
        for food in review.get('foods', []):
            name = food.get('name', 'unknown')
            score = food.get('score')
            if score is not None:
                if name not in food_names:
                    food_names[name] = []
                food_names[name].append(score)
    
    # Find most frequently reviewed foods
    food_frequency = Counter()
    for review in reviews:
        for food in review.get('foods', []):
            name = food.get('name', 'unknown')
            food_frequency[name] += 1
    
    most_common_foods = [
        {
            'name': name,
            'count': count,
            'average_score': round(sum(food_names[name]) / len(food_names[name]), 2) if name in food_names else None
        }
        for name, count in food_frequency.most_common(10)
    ]
    
    return {
        'daily_averages': daily_averages,
        'category_averages': category_averages,
        'overall': overall_stats,
        'most_common_foods': most_common_foods
    }


def print_statistics(stats: Dict, reviews: list):
    """Print formatted statistics to console."""
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    
    # Overall statistics
    if 'overall' in stats and stats['overall']:
        overall = stats['overall']
        print(f"\nOverall:")
        print(f"  Average score: {overall['average_score']}/10")
        print(f"  Total items: {overall['total_items_scored']}")
        print(f"  Score range: {overall['min_score']} - {overall['max_score']}")
    
    # Category averages
    if 'category_averages' in stats and stats['category_averages']:
        print(f"\nAverage scores by category:")
        # Sort by average score descending
        sorted_categories = sorted(
            stats['category_averages'].items(),
            key=lambda x: x[1]['average_score'],
            reverse=True
        )
        for category, data in sorted_categories:
            print(f"  {category:15} {data['average_score']:.2f}/10 ({data['count']} items, range: {data['min_score']}-{data['max_score']})")
    
    # Most common foods
    if 'most_common_foods' in stats and stats['most_common_foods']:
        print(f"\nMost frequently reviewed foods:")
        for food in stats['most_common_foods']:
            avg = f"{food['average_score']:.2f}/10" if food['average_score'] is not None else "N/A"
            print(f"  {food['name']:30} {food['count']:2}x - avg: {avg}")
    
    # Daily averages
    if 'daily_averages' in stats and stats['daily_averages']:
        print(f"\nAverage scores by day:")
        sorted_days = sorted(stats['daily_averages'].items())
        
        # Print in a more compact format (5 per line)
        for i in range(0, len(sorted_days), 5):
            day_group = sorted_days[i:i+5]
            line = "  ".join([f"Day {day:2d}: {score:.2f}" for day, score in day_group])
            print(f"  {line}")
        
        # Calculate trend
        if len(sorted_days) >= 2:
            first_days = sorted_days[:5]
            last_days = sorted_days[-5:]
            first_avg = sum(score for _, score in first_days) / len(first_days)
            last_avg = sum(score for _, score in last_days) / len(last_days)
            trend = last_avg - first_avg
            
            print(f"\n  Trend: ", end="")
            if trend > 0:
                print(f"↑ Improving (+{trend:.2f} points from early days to recent days)")
            elif trend < 0:
                print(f"↓ Declining ({trend:.2f} points from early days to recent days)")
            else:
                print("→ Stable (no significant change)")
    
    # Review coverage
    print(f"\nReview coverage:")
    print(f"  Total reviews: {len(reviews)}")
    with_day = sum(1 for r in reviews if r.get('day_number') is not None)
    print(f"  Reviews with day numbers: {with_day}")
    needs_review = sum(1 for r in reviews if r.get('needs_review', False))
    if needs_review > 0:
        print(f"  WARNING: Flagged for manual review: {needs_review}")


def main():
    """Command-line interface for the script."""
    parser = argparse.ArgumentParser(
        description="Calculate summary statistics from TikTok review data"
    )
    parser.add_argument(
        "reviews_json",
        help="Path to reviews JSON file (e.g., data/username/username_reviews.json)"
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save statistics back to the reviews file"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Save statistics to a separate JSON file"
    )
    
    args = parser.parse_args()
    
    try:
        # Load reviews
        reviews_path = Path(args.reviews_json)
        
        if not reviews_path.exists():
            raise FileNotFoundError(f"Reviews file not found: {args.reviews_json}")
        
        print(f"Loading reviews from {reviews_path}...")
        with open(reviews_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        username = data.get('username', 'unknown')
        reviews = data.get('reviews', [])
        
        print(f"Found {len(reviews)} reviews for @{username}")
        
        # Calculate statistics
        stats = calculate_summary_stats(reviews)
        
        # Print statistics
        print_statistics(stats, reviews)
        
        # Save if requested
        if args.save:
            data['summary_statistics'] = stats
            with open(reviews_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\nSaved statistics to {reviews_path}")
        
        if args.output:
            output_path = Path(args.output)
            output_data = {
                'username': username,
                'generated_at': data.get('generated_at'),
                'summary_statistics': stats
            }
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            print(f"\nSaved statistics to {output_path}")
        
        return 0
        
    except Exception as e:
        print(f"\nError: {e}")
        return 1


if __name__ == "__main__":
    exit(main())

