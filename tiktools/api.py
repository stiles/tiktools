"""
TikAPI client wrapper with convenience methods.
"""

import os
from typing import Optional
from tikapi import TikAPI, ValidationException, ResponseException


class TikAPIClient:
    """
    Wrapper around TikAPI for easier usage.
    
    Example:
        >>> client = TikAPIClient()  # Uses TIKAPI_KEY env var
        >>> profile = client.get_profile("davis_big_dawg")
        >>> posts = client.get_posts(profile['secUid'])
    """
    
    def __init__(self, api_key: Optional[str] = None, sandbox: bool = False):
        """
        Initialize TikAPI client.
        
        Args:
            api_key: TikAPI key (defaults to TIKAPI_KEY environment variable)
            sandbox: Whether to use sandbox server for testing
        """
        self.api_key = api_key or os.getenv('TIKAPI_KEY')
        
        if not self.api_key:
            raise ValueError(
                "API key is required. Provide it via api_key parameter "
                "or TIKAPI_KEY environment variable"
            )
        
        self.api = TikAPI(self.api_key)
        
        if sandbox:
            self.api.set(__sandbox__=True)
    
    def get_profile(self, username: str) -> dict:
        """
        Get user profile information.
        
        Args:
            username: TikTok username (without @)
            
        Returns:
            Dictionary with user profile data including secUid
            
        Raises:
            ValueError: If user profile cannot be found
            ValidationException: If API validation fails
            ResponseException: If API request fails
        """
        try:
            response = self.api.public.check(username=username)
            data = response.json()
            
            if not data or 'userInfo' not in data:
                raise ValueError(f"Could not find user profile for @{username}")
            
            user_info = data['userInfo']
            
            return {
                'username': username,
                'secUid': user_info['user']['secUid'],
                'nickname': user_info['user']['nickname'],
                'videoCount': user_info['stats']['videoCount'],
                'followerCount': user_info['stats']['followerCount'],
                'raw': user_info  # Full data
            }
            
        except (ValidationException, ResponseException) as e:
            raise
    
    def get_posts(self, sec_uid: str, max_count: Optional[int] = None):
        """
        Get posts for a user by their secUid.
        
        Args:
            sec_uid: User's secUid (get from get_profile)
            max_count: Maximum number of posts to retrieve
            
        Yields:
            Post dictionaries from TikAPI
        """
        response = self.api.public.posts(secUid=sec_uid)
        count = 0
        
        while response:
            data = response.json()
            
            if 'itemList' in data:
                for item in data['itemList']:
                    yield item
                    count += 1
                    
                    if max_count and count >= max_count:
                        return
            
            # Get next page
            response = response.next_items()

