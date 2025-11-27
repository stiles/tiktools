"""
Functions for downloading TikTok video thumbnails.
"""

import json
import requests
from pathlib import Path
from typing import Optional, Dict, List


THUMBNAIL_TYPES = {
    "cover": "video.cover",
    "origin": "video.originCover",
    "dynamic": "video.dynamicCover",
    "zoom_240": "video.zoomCover.240",
    "zoom_480": "video.zoomCover.480",
    "zoom_720": "video.zoomCover.720",
    "zoom_960": "video.zoomCover.960",
}


def get_thumbnail_url(post: Dict, thumbnail_type: str = "cover") -> Optional[str]:
    """
    Extract thumbnail URL from post object.
    
    Args:
        post: Post object from TikAPI
        thumbnail_type: Type of thumbnail (cover, origin, dynamic, zoom_240-960)
        
    Returns:
        Thumbnail URL or None if not found
    """
    if thumbnail_type not in THUMBNAIL_TYPES:
        raise ValueError(
            f"Invalid thumbnail_type '{thumbnail_type}'. "
            f"Must be one of: {', '.join(THUMBNAIL_TYPES.keys())}"
        )
    
    path = THUMBNAIL_TYPES[thumbnail_type]
    parts = path.split('.')
    
    obj = post
    for part in parts:
        if not isinstance(obj, dict):
            return None
        obj = obj.get(part)
        if obj is None:
            return None
    
    return obj if isinstance(obj, str) else None


def download_thumbnail(url: str, output_path: Path, timeout: int = 30) -> bool:
    """
    Download thumbnail image from URL.
    
    Args:
        url: Thumbnail URL
        output_path: Path to save image
        timeout: Request timeout in seconds
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Use headers to mimic browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.tiktok.com/',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Sec-Fetch-Dest': 'image',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'cross-site',
        }
        
        response = requests.get(url, headers=headers, timeout=timeout, stream=True)
        response.raise_for_status()
        
        # Write image to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print(f"  X 403 Forbidden - URL signature may have expired")
            print(f"    TikTok thumbnail URLs are time-limited. Try re-fetching posts first.")
        else:
            print(f"  X HTTP Error {e.response.status_code}: {e}")
        return False
    except Exception as e:
        print(f"  X Failed to download thumbnail: {e}")
        return False


def detect_image_extension(url: str, response_headers: Optional[Dict] = None) -> str:
    """
    Detect image file extension from URL or headers.
    
    Args:
        url: Image URL
        response_headers: Optional HTTP response headers
        
    Returns:
        File extension (with dot, e.g., '.jpg')
    """
    # Check URL for explicit extension
    url_lower = url.lower().split('?')[0]  # Remove query params
    for ext in ['.jpg', '.jpeg', '.png', '.webp', '.avif', '.gif']:
        if url_lower.endswith(ext):
            return ext
    
    # Check content-type header if available
    if response_headers:
        content_type = response_headers.get('content-type', '').lower()
        if 'jpeg' in content_type or 'jpg' in content_type:
            return '.jpg'
        elif 'png' in content_type:
            return '.png'
        elif 'webp' in content_type:
            return '.webp'
        elif 'avif' in content_type:
            return '.avif'
        elif 'gif' in content_type:
            return '.gif'
    
    # Check URL for format hints (common in TikTok URLs)
    if '.avif' in url_lower or 'avif' in url_lower:
        return '.avif'
    elif '.webp' in url_lower or 'webp' in url_lower:
        return '.webp'
    
    # Default to jpg for TikTok thumbnails
    return '.jpg'


def download_thumbnails(
    posts_file: Path,
    output_dir: Optional[Path] = None,
    thumbnail_type: str = "cover",
    update_mode: bool = False,
    skip_existing: bool = False
) -> Dict:
    """
    Download thumbnails for all posts in a JSON file.
    
    Args:
        posts_file: Path to posts JSON file
        output_dir: Directory to save thumbnails (defaults to posts_file.parent / "thumbnails")
        thumbnail_type: Type of thumbnail to download (cover, origin, dynamic, zoom_240-960)
        update_mode: Only download thumbnails for new posts
        skip_existing: Skip posts that already have thumbnail files on disk
        
    Returns:
        Dictionary with download results
        
    Example:
        >>> results = download_thumbnails(Path("data/user/user_posts.json"))
        >>> print(f"Downloaded {results['thumbnails_downloaded']} thumbnails")
    """
    if not posts_file.exists():
        raise FileNotFoundError(f"Posts file not found: {posts_file}")
    
    # Load posts
    print(f"Loading posts from {posts_file}...")
    with open(posts_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    username = data.get('username', 'unknown')
    posts = data.get('posts', [])
    
    print(f"Found {len(posts)} posts for @{username}")
    print(f"Thumbnail type: {thumbnail_type}")
    
    # Set up output directory
    if output_dir is None:
        output_dir = posts_file.parent / "thumbnails"
    output_dir.mkdir(exist_ok=True, parents=True)
    
    print(f"Saving thumbnails to {output_dir}/")
    
    # Load existing thumbnail data if in update mode
    existing_thumbnails: List[Dict] = []
    processed_post_ids = set()
    thumbnails_json_path = output_dir / f"{username}_thumbnails.json"
    
    if update_mode and thumbnails_json_path.exists():
        print(f"\nUpdate mode: Loading existing thumbnail data...")
        try:
            with open(thumbnails_json_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                existing_thumbnails = existing_data.get('thumbnails', [])
                processed_post_ids = {t['post_id'] for t in existing_thumbnails}
                print(f"  Found {len(existing_thumbnails)} existing thumbnails")
        except Exception as e:
            print(f"  Warning: Could not load existing thumbnails: {e}")
    
    results = {
        'total_posts': len(posts),
        'thumbnails_found': 0,
        'thumbnails_downloaded': 0,
        'failed': 0,
        'skipped_existing': 0,
        'thumbnails': existing_thumbnails.copy()
    }
    
    # Process each post
    for i, post in enumerate(posts, 1):
        post_id = post.get('id', f'post_{i}')
        desc = post.get('desc', '')[:50]
        
        print(f"\n[{i}/{len(posts)}] Post {post_id}")
        print(f"  Description: {desc}...")
        
        # Skip if already processed
        if update_mode and post_id in processed_post_ids:
            print(f"  Already downloaded, skipping...")
            results['skipped_existing'] += 1
            continue
        
        # Get thumbnail URL
        thumbnail_url = get_thumbnail_url(post, thumbnail_type)
        
        if not thumbnail_url:
            print(f"  X No {thumbnail_type} thumbnail found")
            results['failed'] += 1
            continue
        
        results['thumbnails_found'] += 1
        
        # Detect file extension
        extension = detect_image_extension(thumbnail_url)
        thumbnail_file = output_dir / f"{post_id}{extension}"
        
        # Skip if file already exists (protects manual edits/organization)
        if skip_existing and thumbnail_file.exists():
            print(f"  Thumbnail file exists, skipping to protect existing file...")
            results['skipped_existing'] += 1
            continue
        
        print(f"  Downloading {thumbnail_type} thumbnail...")
        
        # Download thumbnail
        success = download_thumbnail(thumbnail_url, thumbnail_file)
        
        if not success:
            results['failed'] += 1
            continue
        
        results['thumbnails_downloaded'] += 1
        
        # Store thumbnail data
        file_size = thumbnail_file.stat().st_size
        thumbnail_data = {
            'post_id': post_id,
            'description': post.get('desc', ''),
            'create_time': post.get('createTime', 0),
            'thumbnail_type': thumbnail_type,
            'thumbnail_url': thumbnail_url,
            'file_path': str(thumbnail_file),
            'file_size': file_size,
            'extension': extension,
            'stats': post.get('stats', {})
        }
        
        results['thumbnails'].append(thumbnail_data)
        
        print(f"  Saved thumbnail ({file_size / 1024:.1f} KB)")
    
    # Save JSON with all thumbnail data
    with open(thumbnails_json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'username': username,
            'thumbnail_type': thumbnail_type,
            'summary': {
                'total_posts': results['total_posts'],
                'thumbnails_found': results['thumbnails_found'],
                'thumbnails_downloaded': results['thumbnails_downloaded'],
                'failed': results['failed']
            },
            'thumbnails': results['thumbnails']
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved thumbnail data to {thumbnails_json_path}")
    print(f"\nSummary:")
    print(f"  Total posts: {results['total_posts']}")
    print(f"  Thumbnails found: {results['thumbnails_found']}")
    print(f"  Thumbnails downloaded: {results['thumbnails_downloaded']}")
    print(f"  Failed: {results['failed']}")
    print(f"  Skipped (existing): {results['skipped_existing']}")
    
    return results

