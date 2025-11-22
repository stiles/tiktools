"""Tests for post fetching functionality."""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from tiktools.posts import fetch_user_posts


class TestFetchUserPosts:
    """Tests for fetch_user_posts function."""
    
    @patch('tiktools.posts.TikAPIClient')
    def test_fetch_user_posts_basic(self, mock_client_class, sample_post, temp_output_dir):
        """Test basic post fetching."""
        mock_client = Mock()
        mock_client.get_profile.return_value = {
            'nickname': 'Test User',
            'videoCount': 1,
            'secUid': 'test_sec_uid'
        }
        mock_client.get_posts.return_value = iter([sample_post])
        mock_client_class.return_value = mock_client
        
        output_file = temp_output_dir / "posts.json"
        
        result = fetch_user_posts(
            username='test_user',
            api_key='test_key',
            output_file=output_file
        )
        
        assert result['username'] == 'test_user'
        assert result['display_name'] == 'Test User'
        assert result['fetched_count'] == 1
        assert len(result['posts']) == 1
        assert output_file.exists()
        
        # Verify JSON was written correctly
        with open(output_file, 'r') as f:
            saved_data = json.load(f)
        assert saved_data['username'] == 'test_user'
    
    @patch('tiktools.posts.TikAPIClient')
    def test_fetch_user_posts_max_posts(self, mock_client_class, sample_post):
        """Test fetching with max_posts limit."""
        mock_client = Mock()
        mock_client.get_profile.return_value = {
            'nickname': 'Test User',
            'videoCount': 100,
            'secUid': 'test_sec_uid'
        }
        # Create 10 posts but limit should stop at 5
        posts = [sample_post.copy() for _ in range(10)]
        mock_client.get_posts.return_value = iter(posts)
        mock_client_class.return_value = mock_client
        
        result = fetch_user_posts(
            username='test_user',
            api_key='test_key',
            max_posts=5
        )
        
        assert result['fetched_count'] == 5
        assert len(result['posts']) == 5
    
    @patch('tiktools.posts.TikAPIClient')
    def test_fetch_user_posts_update_mode(self, mock_client_class, sample_post, temp_output_dir):
        """Test update mode with existing posts."""
        # Create existing posts file
        existing_posts = {
            'username': 'test_user',
            'posts': [
                {'id': 'old_post_1', 'createTime': 1000},
                {'id': 'old_post_2', 'createTime': 2000}
            ]
        }
        output_file = temp_output_dir / "posts.json"
        with open(output_file, 'w') as f:
            json.dump(existing_posts, f)
        
        # Mock new posts
        new_post = sample_post.copy()
        new_post['id'] = 'new_post_1'
        new_post['createTime'] = 3000
        
        mock_client = Mock()
        mock_client.get_profile.return_value = {
            'nickname': 'Test User',
            'videoCount': 3,
            'secUid': 'test_sec_uid'
        }
        mock_client.get_posts.return_value = iter([new_post])
        mock_client_class.return_value = mock_client
        
        result = fetch_user_posts(
            username='test_user',
            api_key='test_key',
            output_file=output_file,
            update_mode=True
        )
        
        # Should have merged new and existing posts
        assert result['fetched_count'] == 3
        assert len(result['posts']) == 3
        assert result['new_posts'] == 1

