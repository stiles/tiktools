"""Tests for transcript extraction functionality."""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from tiktools.transcripts import (
    parse_webvtt,
    download_subtitle,
    get_best_subtitle
)


class TestParseWebVTT:
    """Tests for WebVTT parsing."""
    
    def test_parse_webvtt_basic(self, sample_webvtt):
        """Test basic WebVTT parsing."""
        result = parse_webvtt(sample_webvtt)
        
        assert "Hello everyone" in result
        assert "test transcript" in result
        assert "multiple lines" in result
        assert "-->" not in result
        assert "WEBVTT" not in result
    
    def test_parse_webvtt_empty(self):
        """Test parsing empty WebVTT content."""
        result = parse_webvtt("")
        assert result == ""
    
    def test_parse_webvtt_no_timestamps(self):
        """Test WebVTT with malformed content."""
        content = "WEBVTT\n\nJust some text without timestamps"
        result = parse_webvtt(content)
        assert "Just some text" in result


class TestDownloadSubtitle:
    """Tests for subtitle downloading."""
    
    @patch('tiktools.transcripts.requests.get')
    def test_download_subtitle_success(self, mock_get, sample_webvtt):
        """Test successful subtitle download."""
        mock_response = Mock()
        mock_response.text = sample_webvtt
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = download_subtitle("https://example.com/subtitle.vtt")
        
        assert result == sample_webvtt
        mock_get.assert_called_once()
    
    @patch('tiktools.transcripts.requests.get')
    def test_download_subtitle_failure(self, mock_get):
        """Test subtitle download failure."""
        mock_get.side_effect = Exception("Network error")
        
        result = download_subtitle("https://example.com/subtitle.vtt")
        
        assert result is None


class TestGetBestSubtitle:
    """Tests for subtitle selection logic."""
    
    def test_get_best_subtitle_asr_preferred_language(self):
        """Test selection of ASR subtitle in preferred language."""
        post = {
            'video': {
                'subtitleInfos': [
                    {
                        'LanguageCodeName': 'eng-US',
                        'Source': 'ASR',
                        'Url': 'https://example.com/eng-asr.vtt'
                    },
                    {
                        'LanguageCodeName': 'spa-ES',
                        'Source': 'ASR',
                        'Url': 'https://example.com/spa-asr.vtt'
                    }
                ]
            }
        }
        
        result = get_best_subtitle(post, preferred_language="eng")
        
        assert result is not None
        assert result['LanguageCodeName'] == 'eng-US'
        assert result['Source'] == 'ASR'
    
    def test_get_best_subtitle_fallback_any_asr(self):
        """Test fallback to any ASR subtitle."""
        post = {
            'video': {
                'subtitleInfos': [
                    {
                        'LanguageCodeName': 'spa-ES',
                        'Source': 'ASR',
                        'Url': 'https://example.com/spa-asr.vtt'
                    }
                ]
            }
        }
        
        result = get_best_subtitle(post, preferred_language="eng")
        
        assert result is not None
        assert result['Source'] == 'ASR'
    
    def test_get_best_subtitle_no_subtitles(self):
        """Test handling of posts without subtitles."""
        post = {'video': {}}
        
        result = get_best_subtitle(post)
        
        assert result is None
    
    def test_get_best_subtitle_prefer_asr_over_mt(self):
        """Test that ASR is preferred over MT (machine translation)."""
        post = {
            'video': {
                'subtitleInfos': [
                    {
                        'LanguageCodeName': 'eng-US',
                        'Source': 'MT',
                        'Url': 'https://example.com/eng-mt.vtt'
                    },
                    {
                        'LanguageCodeName': 'spa-ES',
                        'Source': 'ASR',
                        'Url': 'https://example.com/spa-asr.vtt'
                    }
                ]
            }
        }
        
        result = get_best_subtitle(post, preferred_language="eng")
        
        assert result is not None
        assert result['Source'] == 'ASR'

