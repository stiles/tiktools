# tiktools

**A Python toolkit for TikTok data extraction and analysis using TikAPI.**

Extract post metadata, thumbnails and get video transcription and translation with TikTok's built-in subtitles.

## Features

- **Fetch post metadata** - Download complete post data for any TikTok user
- **Extract transcripts** - Get speech-to-text from videos using TikTok's ASR subtitles
- **Download thumbnails** - Save video thumbnails in multiple sizes and formats
- **Translate transcripts** - Translate transcripts using AWS Translate or other services
- **Incremental updates** - Only fetch new content to save API costs
- **Audio detection** - Flag videos with non-original audio (songs vs. speech)
- **Pip-installable** - Easy to install and use in your projects
- **Extensible** - Build custom analysis tools on top of the core toolkit

## Example in the wild

**[davis.food](https://davis.food)** - A live dashboard tracking @davis_big_dawg's viral school lunch reviews built mostly with tiktools. 

- Automated data collection (posts, transcripts, thumbnails)
- Real-time engagement tracking
- Interactive D3.js charts and statistics
- GitHub Actions workflow for automatic updates

The complete source code is available: [github.com/stiles/davis.food](https://github.com/stiles/davis.food)

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

### 2. Fetch posts, extract transcripts and download thumbnails

```python
from tiktools import fetch_user_posts, extract_transcripts, download_thumbnails
from pathlib import Path

# Fetch posts
posts_data = fetch_user_posts(
    username="davis_big_dawg",
    output_file=Path("data/davis_big_dawg/posts.json")
)

# Extract transcripts
transcript_results = extract_transcripts(
    posts_file=Path("data/davis_big_dawg/posts.json"),
    language="eng"
)

# Download thumbnails
thumbnail_results = download_thumbnails(
    posts_file=Path("data/davis_big_dawg/posts.json"),
    thumbnail_type="origin"  # High quality
)

print(f"Extracted {transcript_results['transcripts_downloaded']} transcripts")
print(f"Downloaded {thumbnail_results['thumbnails_downloaded']} thumbnails")
```

### 3. Use the CLI scripts

```bash
# Fetch all posts
python scripts/fetch_posts.py davis_big_dawg

# Extract transcripts
python scripts/extract_transcripts.py data/davis_big_dawg/davis_big_dawg_posts.json

# Download thumbnails
python scripts/download_thumbnails.py data/davis_big_dawg/davis_big_dawg_posts.json --type origin

# Translate transcripts (requires AWS credentials)
python scripts/translate_transcripts.py data/davis_big_dawg/transcripts/davis_big_dawg_transcripts.json --target en

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

# Only download thumbnails for NEW posts
python scripts/download_thumbnails.py data/davis_big_dawg/davis_big_dawg_posts.json --update

# Only translate NEW transcripts
python scripts/translate_transcripts.py data/davis_big_dawg/transcripts/davis_big_dawg_transcripts.json --target en --update
```

## Output structure

```
data/
└── davis_big_dawg/
    ├── davis_big_dawg_posts.json       # Post metadata
    ├── thumbnails/
    │   ├── 7575304937580547342.jpg     # Individual thumbnails
    │   └── davis_big_dawg_thumbnails.json  # Thumbnail metadata
    └── transcripts/
        ├── 7575304937580547342.txt     # Individual transcripts
        ├── 7575304937580547342.en.txt  # Translated transcripts
        ├── davis_big_dawg_transcripts.json  # All transcripts
        └── davis_big_dawg_translations.json # All translations
```

## Example: Food reviews analysis

**Live example:** [davis.food](https://davis.food) - A production dashboard tracking @davis_big_dawg's viral school lunch reviews with automatic updates.

See `examples/food_reviews/` for a complete example analyzing @davis_big_dawg's school lunch reviews.

The example includes a standalone script that demonstrates the full workflow:

```bash
cd examples/food_reviews

# Install tiktools and dependencies
pip install tiktools openai

# Set up API keys
export TIKAPI_KEY="your_tikapi_key_here"
export OPENAI_API_KEY="your_openai_key_here"

# Fetch posts, transcripts, thumbnails and extract review data
python fetch_davis_archive.py --extract-reviews --download-thumbnails

# Calculate statistics
python calculate_stats.py data/davis_big_dawg/davis_big_dawg_reviews.json
```

Features:
- Fetches all posts and transcripts for a TikTok user
- Downloads video thumbnails (URLs expire quickly!)
- Extracts structured review data using OpenAI
- Calculates statistics by category and day
- Update mode to only fetch new content

See the example README for full documentation and customization options.

**Production deployment:** The complete [davis.food source code](https://github.com/stiles/davis.food) demonstrates how to build a production dashboard with GitHub Actions, Eleventy, D3.js charts and automated data updates.

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

#### `download_thumbnails()`

Download video thumbnails for posts.

```python
from tiktools import download_thumbnails
from pathlib import Path

results = download_thumbnails(
    posts_file=Path("posts.json"),
    output_dir=None,  # Defaults to posts_file.parent/thumbnails
    thumbnail_type="cover",  # or "origin", "dynamic", "zoom_960"
    update_mode=False,  # Only download for new posts
    skip_existing=False  # Skip if file exists
)
```

**Important:** TikTok's thumbnail URLs have time-limited signatures and expire quickly (typically within hours). For best results, download thumbnails immediately after fetching posts:

```python
# Recommended: Download thumbnails while URLs are fresh
data = fetch_user_posts(
    username="davis_big_dawg",
    output_file=Path("data/davis_big_dawg/posts.json"),
    download_thumbnails=True,
    thumbnail_type="origin"
)
```

Or use the CLI:
```bash
python scripts/fetch_posts.py davis_big_dawg --download-thumbnails --thumbnail-type origin
```

**Thumbnail types:**
- `cover` - Standard cover image (default)
- `origin` - Original quality cover (highest quality)
- `dynamic` - Animated cover
- `zoom_240`, `zoom_480`, `zoom_720`, `zoom_960` - Specific resolutions

#### `translate_transcripts()`

Translate transcripts to multiple languages.

```python
from tiktools import translate_transcripts
from pathlib import Path

results = translate_transcripts(
    transcripts_file=Path("transcripts/user_transcripts.json"),
    target_languages=["en", "es"],
    service="aws",  # AWS Translate
    output_dir=None,  # Defaults to transcripts_file.parent
    update_mode=False,  # Only translate new transcripts
    estimate_only=False,  # Estimate costs without translating
    source_language=None  # Auto-detected if None
)
```

**Translation service setup:**

For AWS Translate, configure AWS credentials:
```bash
# Option 1: AWS CLI
aws configure

# Option 2: Environment variables
export AWS_ACCESS_KEY_ID="your_key"
export AWS_SECRET_ACCESS_KEY="your_secret"
export AWS_DEFAULT_REGION="us-east-1"
```

**Cost estimation:**
```python
# Estimate costs before translating
results = translate_transcripts(
    transcripts_file=Path("transcripts/user_transcripts.json"),
    target_languages=["en", "es", "fr"],
    estimate_only=True
)
print(f"Estimated cost: ${results['estimated_cost']:.4f} USD")
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

Core dependencies:
- `tikapi` - TikTok API client
- `requests` - HTTP requests
- `pathlib` - File path handling

Optional dependencies:
- `boto3` - AWS Translate for translation features (install with: `pip install boto3`)

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