"""Tests for TikAPI client wrapper."""

import os
import pytest
from unittest.mock import Mock, patch

from tiktools.api import TikAPIClient


class TestTikAPIClient:
    """Tests for TikAPIClient class."""
    
    @patch.dict(os.environ, {'TIKAPI_KEY': 'test_key'})
    def test_init_with_env_var(self):
        """Test initialization with environment variable."""
        client = TikAPIClient()
        assert client.api is not None
    
    def test_init_with_api_key(self):
        """Test initialization with explicit API key."""
        client = TikAPIClient(api_key='test_key')
        assert client.api is not None
    
    @patch.dict(os.environ, {}, clear=True)
    def test_init_without_api_key_raises(self):
        """Test that missing API key raises ValueError."""
        with pytest.raises(ValueError, match="API key is required"):
            TikAPIClient()
    
    def test_init_sandbox_mode(self):
        """Test initialization in sandbox mode."""
        client = TikAPIClient(api_key='test_key', sandbox=True)
        assert client.api is not None
    
    @patch('tiktools.api.TikAPI')
    def test_get_profile(self, mock_tikapi):
        """Test profile fetching."""
        mock_api = Mock()
        mock_api.public.check.return_value.json.return_value = {
            'userInfo': {
                'user': {
                    'nickname': 'Test User',
                    'secUid': 'test_sec_uid',
                    'id': '123456'
                },
                'stats': {
                    'videoCount': 100,
                    'followerCount': 5000
                }
            }
        }
        mock_tikapi.return_value = mock_api
        
        client = TikAPIClient(api_key='test_key')
        result = client.get_profile('test_user')
        
        assert result['nickname'] == 'Test User'
        assert result['secUid'] == 'test_sec_uid'
        assert result['videoCount'] == 100
        assert result['followerCount'] == 5000
    
    @patch('tiktools.api.TikAPI')
    def test_get_posts(self, mock_tikapi):
        """Test post iteration."""
        mock_api = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            'itemList': [
                {'id': '1', 'desc': 'Post 1'},
                {'id': '2', 'desc': 'Post 2'}
            ],
            'hasMore': False
        }
        mock_api.public.posts.return_value = mock_response
        mock_tikapi.return_value = mock_api
        
        client = TikAPIClient(api_key='test_key')
        posts = list(client.get_posts('test_sec_uid', max_count=2))
        
        assert len(posts) == 2
        assert posts[0]['id'] == '1'
        assert posts[1]['id'] == '2'

