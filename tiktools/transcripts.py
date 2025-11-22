"""
Functions for extracting transcripts from TikTok videos using subtitle files.
"""

import json
import requests
from pathlib import Path
from typing import Optional, Dict, List


def parse_webvtt(content: str) -> str:
    """
    Parse WebVTT subtitle file and extract just the text.
    
    Args:
        content: Raw WebVTT file content
        
    Returns:
        Clean transcript text with timestamps removed
    """
    lines = content.strip().split('\n')
    transcript_lines = []
    
    in_content = False
    for line in lines:
        line = line.strip()
        
        if line.startswith('WEBVTT'):
            in_content = True
            continue
        
        if '-->' in line or not line or line.isdigit():
            continue
        
        if in_content and line:
            transcript_lines.append(line)
    
    return ' '.join(transcript_lines)


def download_subtitle(url: str, timeout: int = 30) -> Optional[str]:
    """
    Download subtitle file from URL.
    
    Args:
        url: Subtitle file URL
        timeout: Request timeout in seconds
        
    Returns:
        Subtitle file content as string, or None if download fails
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"  X Failed to download subtitle: {e}")
        return None


def get_best_subtitle(post: Dict, preferred_language: str = "eng") -> Optional[Dict]:
    """
    Get the best available subtitle for a post.
    
    Prioritizes ASR (automatic speech recognition) over MT (machine translation).
    
    Args:
        post: Post object from TikAPI
        preferred_language: Preferred language code (default: "eng" for English)
        
    Returns:
        Subtitle info dict or None if no suitable subtitle found
    """
    if 'video' not in post or 'subtitleInfos' not in post['video']:
        return None
    
    subtitles = post['video']['subtitleInfos']
    
    # First try ASR in preferred language
    for subtitle in subtitles:
        lang_code = subtitle.get('LanguageCodeName', '').split('-')[0]
        if lang_code == preferred_language and subtitle.get('Source') == 'ASR':
            return subtitle
    
    # Fall back to any ASR subtitle
    for subtitle in subtitles:
        if subtitle.get('Source') == 'ASR':
            return subtitle
    
    # Last resort: any subtitle in preferred language
    for subtitle in subtitles:
        lang_code = subtitle.get('LanguageCodeName', '').split('-')[0]
        if lang_code == preferred_language:
            return subtitle
    
    return None


def extract_transcripts(
    posts_file: Path,
    output_dir: Optional[Path] = None,
    output_format: str = "individual",
    language: str = "eng",
    update_mode: bool = False
) -> Dict:
    """
    Extract transcripts from all posts in a JSON file.
    
    Args:
        posts_file: Path to posts JSON file
        output_dir: Directory to save transcripts (defaults to posts_file.parent / "transcripts")
        output_format: Either "individual" (one file per post) or "combined" (single file)
        language: Preferred language code for subtitles
        update_mode: Only process new posts
        
    Returns:
        Dictionary with extraction results
        
    Example:
        >>> results = extract_transcripts(Path("data/user/user_posts.json"))
        >>> print(f"Downloaded {results['transcripts_downloaded']} transcripts")
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
    
    # Set up output directory
    if output_dir is None:
        output_dir = posts_file.parent / "transcripts"
    output_dir.mkdir(exist_ok=True, parents=True)
    
    print(f"Saving transcripts to {output_dir}/")
    
    # Load existing transcripts if in update mode
    existing_transcripts: List[Dict] = []
    processed_post_ids = set()
    transcripts_json_path = output_dir / f"{username}_transcripts.json"
    
    if update_mode and transcripts_json_path.exists():
        print(f"\nUpdate mode: Loading existing transcripts...")
        try:
            with open(transcripts_json_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                existing_transcripts = existing_data.get('transcripts', [])
                processed_post_ids = {t['post_id'] for t in existing_transcripts}
                print(f"  Found {len(existing_transcripts)} existing transcripts")
        except Exception as e:
            print(f"  Warning: Could not load existing transcripts: {e}")
    
    results = {
        'total_posts': len(posts),
        'transcripts_found': 0,
        'transcripts_downloaded': 0,
        'failed': 0,
        'skipped_existing': 0,
        'transcripts': existing_transcripts.copy()
    }
    
    # Process each post
    for i, post in enumerate(posts, 1):
        post_id = post.get('id', f'post_{i}')
        desc = post.get('desc', '')[:50]
        
        print(f"\n[{i}/{len(posts)}] Post {post_id}")
        print(f"  Description: {desc}...")
        
        # Skip if already processed
        if update_mode and post_id in processed_post_ids:
            print(f"  Already transcribed, skipping...")
            results['skipped_existing'] += 1
            continue
        
        # Check audio type
        music = post.get('music', {})
        is_original_audio = music.get('original', False)
        music_author = music.get('authorName', '')
        
        # Get subtitle
        subtitle = get_best_subtitle(post, language)
        
        if not subtitle:
            print("  X No suitable subtitle found")
            results['failed'] += 1
            continue
        
        results['transcripts_found'] += 1
        
        subtitle_url = subtitle.get('Url')
        lang_name = subtitle.get('LanguageCodeName', 'unknown')
        source = subtitle.get('Source', 'unknown')
        
        print(f"  Found subtitle: {lang_name} ({source})")
        
        if not is_original_audio:
            print(f"  WARNING: Non-original audio - may contain song lyrics")
        
        # Download subtitle
        subtitle_content = download_subtitle(subtitle_url)
        
        if not subtitle_content:
            results['failed'] += 1
            continue
        
        # Parse transcript
        transcript = parse_webvtt(subtitle_content)
        
        if not transcript:
            print("  X Failed to parse transcript")
            results['failed'] += 1
            continue
        
        results['transcripts_downloaded'] += 1
        
        # Store transcript data
        transcript_data = {
            'post_id': post_id,
            'description': post.get('desc', ''),
            'create_time': post.get('createTime', 0),
            'transcript': transcript,
            'language': lang_name,
            'source': source,
            'is_original_audio': is_original_audio,
            'music_author': music_author,
            'stats': post.get('stats', {})
        }
        
        results['transcripts'].append(transcript_data)
        
        # Save individual file
        if output_format in ["individual", "both"]:
            transcript_file = output_dir / f"{post_id}.txt"
            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write(f"Post ID: {post_id}\n")
                f.write(f"Description: {post.get('desc', '')}\n")
                f.write(f"Language: {lang_name} ({source})\n")
                f.write(f"Original Audio: {is_original_audio}\n")
                if not is_original_audio:
                    f.write(f"WARNING: Non-original audio - may contain song lyrics\n")
                f.write(f"\n{transcript}\n")
            
            print(f"  Saved transcript ({len(transcript)} chars)")
    
    # Save combined file if requested
    if output_format in ["combined", "both"]:
        combined_file = output_dir / f"{username}_all_transcripts.txt"
        with open(combined_file, 'w', encoding='utf-8') as f:
            f.write(f"Transcripts for @{username}\n")
            f.write(f"Total transcripts: {results['transcripts_downloaded']}\n")
            f.write("=" * 80 + "\n\n")
            
            for t_data in results['transcripts']:
                f.write(f"Post ID: {t_data['post_id']}\n")
                f.write(f"Description: {t_data['description']}\n")
                f.write(f"Language: {t_data['language']} ({t_data['source']})\n")
                f.write("-" * 80 + "\n")
                f.write(f"{t_data['transcript']}\n")
                f.write("=" * 80 + "\n\n")
        
        print(f"\nSaved combined transcripts to {combined_file}")
    
    # Save JSON with all transcript data
    with open(transcripts_json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'username': username,
            'summary': {
                'total_posts': results['total_posts'],
                'transcripts_found': results['transcripts_found'],
                'transcripts_downloaded': results['transcripts_downloaded'],
                'failed': results['failed']
            },
            'transcripts': results['transcripts']
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved transcript data to {transcripts_json_path}")
    
    return results

