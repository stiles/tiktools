# tiktools

**A Python toolkit for TikTok data extraction and analysis using TikAPI.**

Extract post metadata, transcribe videos using TikTok's built-in subtitles and analyze content at scale. Perfect for researchers, journalists and data analysts.

[![PyPI version](https://badge.fury.io/py/tiktools.svg)](https://badge.fury.io/py/tiktools)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Fetch post metadata** - Download complete post data for any TikTok user
- **Extract transcripts** - Get speech-to-text from videos using TikTok's ASR subtitles
- **Incremental updates** - Only fetch new content to save API costs
- **Audio detection** - Flag videos with non-original audio (songs vs. speech)
- **Pip-installable** - Easy to install and use in your projects
- **Extensible** - Build custom analysis tools on top of the core toolkit

## Installation

```bash
pip install tiktools
```

## Quick start

### 1. Set up API keys

TikTools requires a [TikAPI](https://tikapi.io) key for core functionality:

```bash
export TIKAPI_KEY="your_tikapi_key_here"
```

For testing, you can use the sandbox key: `DemoAPIKeyTokenSeHYGXDfd4SFD320Sc39Asd0Sc39Asd4s`

### 2. Fetch posts and extract transcripts

```python
from tiktools import fetch_user_posts, extract_transcripts
from pathlib import Path

# Fetch posts
posts_data = fetch_user_posts(
    username="davis_big_dawg",
    output_file=Path("data/davis_big_dawg/posts.json")
)

# Extract transcripts
results = extract_transcripts(
    posts_file=Path("data/davis_big_dawg/posts.json"),
    language="eng"
)

print(f"Extracted {results['transcripts_downloaded']} transcripts")
```

### 3. Use the CLI scripts

```bash
# Fetch all posts
python scripts/fetch_posts.py davis_big_dawg

# Extract transcripts
python scripts/extract_transcripts.py data/davis_big_dawg/davis_big_dawg_posts.json

# See generic analysis template
python scripts/analyze.py data/davis_big_dawg/transcripts/davis_big_dawg_transcripts.json
```

## Incremental updates

Save API costs by only fetching new content:

```bash
# Only fetch NEW posts
python scripts/fetch_posts.py davis_big_dawg --update

# Only transcribe NEW posts
python scripts/extract_transcripts.py data/davis_big_dawg/davis_big_dawg_posts.json --update
```

## Output structure

```
data/
└── davis_big_dawg/
    ├── davis_big_dawg_posts.json       # Post metadata
    └── transcripts/
        ├── 7575304937580547342.txt     # Individual transcripts
        └── davis_big_dawg_transcripts.json  # All transcripts
```

## Example: Food reviews analysis

See `examples/food_reviews/` for a complete example that:
- Extracts structured review data using OpenAI
- Calculates statistics by category and day
- Handles scoring and categorization

```bash
cd examples/food_reviews
python extract_reviews.py ../../data/davis_big_dawg/transcripts/davis_big_dawg_transcripts.json
python calculate_stats.py ../../data/davis_big_dawg/davis_big_dawg_reviews.json
```

## API Reference

### Core functions

#### `fetch_user_posts()`

Fetch TikTok post metadata for a user.

```python
from tiktools import fetch_user_posts
from pathlib import Path

data = fetch_user_posts(
    username="davis_big_dawg",
    api_key=None,  # Uses TIKAPI_KEY env var
    max_posts=100,  # Limit number of posts
    output_file=Path("output.json"),
    sandbox=False,
    update_mode=False  # Only fetch new posts
)
```

#### `extract_transcripts()`

Extract transcripts from TikTok videos using subtitle files.

```python
from tiktools import extract_transcripts
from pathlib import Path

results = extract_transcripts(
    posts_file=Path("posts.json"),
    output_dir=None,  # Defaults to posts_file.parent/transcripts
    output_format="individual",  # or "combined" or "both"
    language="eng",
    update_mode=False  # Only process new posts
)
```

#### `get_best_subtitle()`

Get the best available subtitle for a post (prioritizes ASR over MT).

```python
from tiktools import get_best_subtitle

subtitle = get_best_subtitle(post, preferred_language="eng")
if subtitle:
    print(f"Found {subtitle['LanguageCodeName']} ({subtitle['Source']})")
```

### API Client

```python
from tiktools import TikAPIClient

client = TikAPIClient()  # Uses TIKAPI_KEY env var

# Get profile
profile = client.get_profile("davis_big_dawg")
print(profile['nickname'], profile['videoCount'])

# Iterate through posts
for post in client.get_posts(profile['secUid'], max_count=10):
    print(post['desc'])
```

## Transcript limitations

TikTok's automatic speech recognition (ASR) has some limitations:

1. **Speech recognition errors**: May misinterpret words (e.g., "Baha Blast" → "Brawha Blast")
2. **Non-speech audio**: Videos using TikTok sounds may contain song lyrics instead of speech

**Recommendations**:
- Filter by `is_original_audio: true` for speech-only content
- Manually verify proper nouns and brand names for journalistic work
- Check the `needs_review` flag if using AI extraction

## Requirements

- Python 3.8+
- TikAPI key (get one at [tikapi.io](https://tikapi.io))
- Optional: OpenAI API key (for AI-powered analysis examples)

## Dependencies

- `tikapi` - TikTok API client
- `requests` - HTTP requests
- `pathlib` - File path handling

## Development

```bash
# Clone the repository
git clone https://github.com/stiles/tiktools.git
cd tiktools

# Install in development mode
pip install -e .

# Run tests
pytest tests/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Built on top of [TikAPI](https://tikapi.io)
- Inspired by the need for more TikTok research tools

## Support

- Email: mattstiles@gmail.com
- Issues: [GitHub Issues](https://github.com/stiles/tiktools/issues)
- Discussions: [GitHub Discussions](https://github.com/stiles/tiktools/discussions)

## Citation

If you use this toolkit in your research, please cite:

```bibtex
@software{tiktools2025,
  author = {Matt Stiles},
  title = {tiktools: A Python toolkit for TikTok data extraction and analysis},
  year = {2025},
  url = {https://github.com/stiles/tiktools}
}
```

