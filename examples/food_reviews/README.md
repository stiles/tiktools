# Food reviews analysis example

This example demonstrates how to use `tiktools` to analyze food review videos on TikTok.

## About this example

This analysis was built to extract structured data from @davis_big_dawg's school lunch review videos. Each video follows a format like "Day 30 of reviewing school food" and rates multiple food items.

The scripts use OpenAI's API to extract:
- Day number of the review
- Food items with names, categories, scores and comments
- Flags for posts needing manual review

## Files

- `extract_reviews.py` - Extract structured review data using OpenAI
- `calculate_stats.py` - Calculate statistics from extracted reviews
- `sample_output/` - Example output data (sanitized subset)

## Usage

### 1. Extract reviews

First, make sure you have transcripts from the main toolkit:

```bash
# From the repository root
python scripts/fetch_posts.py davis_big_dawg
python scripts/extract_transcripts.py data/davis_big_dawg/davis_big_dawg_posts.json
```

Then extract structured review data:

```bash
cd examples/food_reviews
python extract_reviews.py ../../data/davis_big_dawg/transcripts/davis_big_dawg_transcripts.json
```

This requires an OpenAI API key (set `OPENAI_API_KEY` environment variable).

### 2. Calculate statistics

```bash
python calculate_stats.py ../../data/davis_big_dawg/davis_big_dawg_reviews.json
```

This script has no API dependencies and runs instantly.

## Example output

### Extracted review

```json
{
  "post_id": "7575304937580547342",
  "day_number": 30,
  "needs_review": false,
  "foods": [
    {
      "name": "burger on a biscuit",
      "category": "main_dish",
      "score": 6,
      "comments": "Kind of dry but still pretty good..."
    },
    {
      "name": "Tropical Lime Baha Blast",
      "category": "drink",
      "score": 8,
      "comments": "One of my favorite sodas..."
    }
  ]
}
```

### Statistics

```
Overall:
  Average score: 6.44/10
  Total items: 131
  
Average scores by category:
  drink    7.58/10 (13 items)
  dessert  7.40/10 (5 items)
  side     5.91/10 (47 items)
  
Trend: ↑ Improving (+0.42 points)
```

## Adapting this example

You can use this as a template for other types of content analysis:

1. Modify the OpenAI prompt in `extract_reviews.py` to extract different information
2. Adjust the categories and scoring system to match your content
3. Update `calculate_stats.py` to compute relevant statistics

## Requirements

- OpenAI API key (for `extract_reviews.py`)
- All dependencies from main `tiktools` package

## Notes

**Transcript limitations**: TikTok's ASR may misinterpret words (e.g., "Baha Blast" → "Brawha Blast"). For journalistic or public-facing analysis, manually verify transcripts for proper nouns and brand names.

