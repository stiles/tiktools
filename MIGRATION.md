# Migration from scripts/tiktok to tiktools

This document explains the changes from the original `scripts/tiktok` directory to the new `tiktools` package.

## What changed

### Structure

**Before** (`scripts/tiktok/`):
```
scripts/tiktok/
├── get_user_posts.py
├── get_transcripts.py
├── extract_reviews.py
├── calculate_stats.py
└── data/
```

**After** (`tiktools/`):
```
tiktools/
├── tiktools/                # Installable package
│   ├── __init__.py
│   ├── api.py              # TikAPI wrapper
│   ├── posts.py            # Post fetching logic
│   └── transcripts.py      # Transcript extraction
├── scripts/                 # CLI tools
│   ├── fetch_posts.py
│   ├── extract_transcripts.py
│   └── analyze.py
├── examples/
│   └── food_reviews/        # Your davis_big_dawg analysis
│       ├── extract_reviews.py
│       ├── calculate_stats.py
│       ├── README.md
│       └── sample_output/
├── tests/
├── README.md
├── pyproject.toml           # Pip installation config
└── requirements.txt
```

## Benefits of the new structure

1. **Pip-installable**: `pip install tiktools` (or `pip install -e .` for development)
2. **Reusable**: Import functions in your own scripts
3. **Clear separation**: Generic toolkit vs specific examples
4. **Better documentation**: Comprehensive README and examples
5. **Standard structure**: Follows Python packaging best practices

## Code changes

### Old way (scripts/tiktok)

```python
# Had to run the script directly
python get_user_posts.py davis_big_dawg
python get_transcripts.py data/davis_big_dawg/davis_big_dawg_posts.json
```

### New way (tiktools)

**Option 1: Use as a library**
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
    posts_file=Path("data/davis_big_dawg/posts.json")
)
```

**Option 2: Use CLI scripts**
```bash
python scripts/fetch_posts.py davis_big_dawg
python scripts/extract_transcripts.py data/davis_big_dawg/davis_big_dawg_posts.json
```

**Option 3: Install and use from anywhere**
```bash
cd /Users/mstiles/github/tiktools
pip install -e .

# Now you can import from any Python script
python -c "from tiktools import TikAPIClient; print('Works!')"
```

## Next steps

### 1. Test the new package

```bash
cd /Users/mstiles/github/tiktools

# Install in development mode
pip install -e .

# Test basic functionality
python scripts/fetch_posts.py davis_big_dawg --help
```

### 2. Run the food reviews example

```bash
# If you have existing data in scripts/tiktok/data/
# You can use it directly or re-fetch

cd examples/food_reviews

# Extract reviews (requires OPENAI_API_KEY)
python extract_reviews.py ../../data/davis_big_dawg/transcripts/davis_big_dawg_transcripts.json

# Calculate stats
python calculate_stats.py ../../data/davis_big_dawg/davis_big_dawg_reviews.json
```

### 3. Create a GitHub repository

```bash
cd /Users/mstiles/github/tiktools

# Already initialized! Just add a remote
git remote add origin https://github.com/mattystiles/tiktools.git
git push -u origin main
```

### 4. Publish to PyPI (when ready)

```bash
# Build the package
pip install build twine
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

## Data migration

Your existing data in `scripts/tiktok/data/` can stay there or be moved:

```bash
# Option 1: Copy data to new location
cp -r /Users/mstiles/github/scripts/tiktok/data/* /Users/mstiles/github/tiktools/data/

# Option 2: Use absolute paths in scripts
python scripts/fetch_posts.py davis_big_dawg --output /Users/mstiles/github/scripts/tiktok/data/davis_big_dawg/davis_big_dawg_posts.json
```

## FAQs

**Q: Can I still use the old scripts?**  
A: Yes! They're unchanged in `scripts/tiktok/`. But the new package is better for long-term use.

**Q: Do I need to republish this as `tiktools`?**  
A: Only if you want others to be able to `pip install tiktools`. It's perfectly fine to use it locally with `pip install -e .`

**Q: What about the OpenAPI spec file?**  
A: It's not needed in the package since TikAPI handles that. Keep it in `scripts/` for reference.

**Q: Should I delete the old `scripts/tiktok` directory?**  
A: Not yet! Keep it as a backup until you've verified everything works in the new structure.

## Support

If you run into issues, check:
1. README.md - Main documentation
2. examples/food_reviews/README.md - Example-specific docs
3. This file - Migration-specific questions

