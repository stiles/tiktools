# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Test suite with 21 tests covering core functionality
- Tests for API client, transcript extraction, post fetching and integration
- Test coverage reporting with pytest-cov (55% overall coverage)
- Added build and twine to dev dependencies for easier publishing

## [0.1.0] - 2025-11-22

### Added
- Initial release of tiktools
- Core TikAPI client wrapper for authenticated API access
- Post metadata fetching with incremental update support
- Transcript extraction using TikTok's ASR (automatic speech recognition) subtitles
- WebVTT subtitle parsing and text extraction
- Original audio detection to flag potential song lyrics
- Incremental update mode for both posts and transcripts to save API costs
- CLI scripts for fetch_posts, extract_transcripts and analyze
- Food reviews example demonstrating AI-powered content extraction with OpenAI
- Comprehensive documentation and README
- MIT license

### Features
- **Post fetching**: Download complete post metadata for any TikTok user
- **Transcript extraction**: Get speech-to-text from videos using TikTok's built-in subtitles
- **Incremental updates**: Only fetch new content to save API costs
- **Audio detection**: Flag videos with non-original audio (songs vs. speech)
- **Pip-installable**: Easy installation via pip
- **Extensible**: Build custom analysis tools on top of the core toolkit

### Requirements
- Python 3.8+
- TikAPI key for core functionality
- Optional: OpenAI API key for AI-powered analysis examples

[Unreleased]: https://github.com/stiles/tiktools/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/stiles/tiktools/releases/tag/v0.1.0

