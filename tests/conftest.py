"""Shared test fixtures and configuration."""

import pytest
from pathlib import Path


@pytest.fixture
def sample_post():
    """Sample TikTok post data for testing."""
    return {
        'id': '7575304937580547342',
        'desc': 'Test post description',
        'createTime': 1234567890,
        'video': {
            'subtitleInfos': [
                {
                    'LanguageCodeName': 'eng-US',
                    'Url': 'https://example.com/subtitle.vtt',
                    'Source': 'ASR',
                    'Size': 1024
                }
            ]
        },
        'music': {
            'original': True,
            'authorName': 'Test User'
        },
        'stats': {
            'playCount': 1000,
            'diggCount': 50,
            'commentCount': 10
        }
    }


@pytest.fixture
def sample_posts_data(sample_post):
    """Sample posts JSON data structure."""
    return {
        'username': 'test_user',
        'display_name': 'Test User',
        'sec_uid': 'test_sec_uid',
        'total_videos': 100,
        'fetched_count': 1,
        'new_posts': 1,
        'posts': [sample_post]
    }


@pytest.fixture
def sample_webvtt():
    """Sample WebVTT subtitle content."""
    return """WEBVTT

00:00:00.000 --> 00:00:02.000
Hello everyone, this is a test

00:00:02.000 --> 00:00:05.000
transcript for testing purposes.

00:00:05.000 --> 00:00:08.000
It contains multiple lines of text.
"""


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary output directory for tests."""
    output_dir = tmp_path / "test_output"
    output_dir.mkdir()
    return output_dir

