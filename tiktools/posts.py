"""
Functions for fetching and managing TikTok post metadata.
"""

import json
from pathlib import Path
from typing import Optional, Dict, List
from tikapi import ValidationException, ResponseException

from .api import TikAPIClient


def fetch_user_posts(
    username: str,
    api_key: Optional[str] = None,
    max_posts: Optional[int] = None,
    output_file: Optional[Path] = None,
    sandbox: bool = False,
    update_mode: bool = False
) -> Dict:
    """
    Retrieve all posts for a given TikTok username.
    
    Args:
        username: TikTok username to fetch posts for
        api_key: TikAPI API key (defaults to TIKAPI_KEY env var)
        max_posts: Maximum number of posts to retrieve (None for all)
        output_file: Path to save JSON output
        sandbox: Whether to use sandbox server for testing
        update_mode: Only fetch new posts since last run
        
    Returns:
        Dictionary containing all posts and metadata
        
    Example:
        >>> data = fetch_user_posts("davis_big_dawg")
        >>> print(f"Fetched {len(data['posts'])} posts")
    """
    # Initialize API client
    client = TikAPIClient(api_key=api_key, sandbox=sandbox)
    
    print(f"Fetching profile information for @{username}...")
    
    try:
        # Get user profile
        profile = client.get_profile(username)
        
        print(f"Found user: {profile['nickname']} (@{username})")
        print(f"Total videos: {profile['videoCount']}")
        
        # Check for existing posts in update mode
        existing_posts: List[Dict] = []
        most_recent_time = 0
        existing_post_ids = set()
        
        if update_mode and output_file and output_file.exists():
            print(f"\n🔄 Update mode: Loading existing posts from {output_file}...")
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    existing_posts = existing_data.get('posts', [])
                    existing_post_ids = {p['id'] for p in existing_posts}
                    
                    if existing_posts:
                        most_recent_time = max(p.get('createTime', 0) for p in existing_posts)
                        print(f"  Found {len(existing_posts)} existing posts")
                        print(f"  Most recent post: {most_recent_time}")
            except Exception as e:
                print(f"  ⚠ Warning: Could not load existing posts: {e}")
                print(f"  Proceeding with full fetch...")
        
        print(f"Fetching posts...")
        
        # Fetch posts
        all_posts: List[Dict] = []
        new_posts_count = 0
        should_stop = False
        
        for iteration, post in enumerate(client.get_posts(profile['secUid']), 1):
            # In update mode, stop when we hit posts we already have
            if update_mode and most_recent_time > 0:
                item_time = post.get('createTime', 0)
                item_id = post.get('id')
                
                if item_time <= most_recent_time or item_id in existing_post_ids:
                    print(f"Iteration {iteration}: Reached existing posts, stopping")
                    break
                
                all_posts.append(post)
                new_posts_count += 1
                
                if new_posts_count % 10 == 0:
                    print(f"Iteration {iteration}: Found {new_posts_count} new posts")
            else:
                all_posts.append(post)
                
                if len(all_posts) % 50 == 0:
                    print(f"Iteration {iteration}: Retrieved {len(all_posts)} posts")
            
            # Check max_posts limit
            if max_posts and len(all_posts) >= max_posts:
                all_posts = all_posts[:max_posts]
                print(f"Reached max_posts limit of {max_posts}")
                break
        
        # Merge with existing posts if in update mode
        if update_mode and existing_posts:
            print(f"\n🔄 Merging {len(all_posts)} new posts with {len(existing_posts)} existing posts...")
            all_posts = all_posts + existing_posts
            print(f"  Total posts after merge: {len(all_posts)}")
        
        # Prepare output data
        output_data = {
            "username": username,
            "display_name": profile['nickname'],
            "sec_uid": profile['secUid'],
            "total_videos": profile['videoCount'],
            "fetched_count": len(all_posts),
            "new_posts": new_posts_count if update_mode else len(all_posts),
            "posts": all_posts
        }
        
        # Save to file if specified
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            if update_mode and new_posts_count > 0:
                print(f"\n✓ Successfully saved {len(all_posts)} total posts ({new_posts_count} new) to {output_file}")
            elif update_mode:
                print(f"\n✓ No new posts found. File unchanged: {output_file}")
            else:
                print(f"\n✓ Successfully saved {len(all_posts)} posts to {output_file}")
            print(f"  File size: {output_file.stat().st_size / 1024:.2f} KB")
        
        return output_data
        
    except (ValidationException, ResponseException) as e:
        print(f"API error: {e}")
        raise

