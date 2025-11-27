"""
Functions for translating TikTok transcripts using cloud translation services.
"""

import json
from pathlib import Path
from typing import Optional, Dict, List, Protocol
from abc import ABC, abstractmethod


class TranslationService(ABC):
    """Abstract base class for translation services."""
    
    @abstractmethod
    def translate(self, text: str, source_language: str, target_language: str) -> str:
        """
        Translate text from source to target language.
        
        Args:
            text: Text to translate
            source_language: Source language code (e.g., 'es', 'en')
            target_language: Target language code (e.g., 'en', 'es')
            
        Returns:
            Translated text
        """
        pass
    
    @abstractmethod
    def detect_language(self, text: str) -> str:
        """
        Detect the language of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code (e.g., 'en', 'es', 'fr')
        """
        pass
    
    @abstractmethod
    def estimate_cost(self, char_count: int) -> float:
        """
        Estimate translation cost in USD.
        
        Args:
            char_count: Number of characters to translate
            
        Returns:
            Estimated cost in USD
        """
        pass


class AWSTranslateService(TranslationService):
    """AWS Translate translation service."""
    
    def __init__(self, region_name: str = "us-east-1"):
        """
        Initialize AWS Translate client.
        
        Args:
            region_name: AWS region name
            
        Raises:
            ImportError: If boto3 is not installed
            ValueError: If AWS credentials are not configured
        """
        try:
            import boto3
            from botocore.exceptions import NoCredentialsError
        except ImportError:
            raise ImportError(
                "boto3 is required for AWS Translate. Install it with: pip install boto3"
            )
        
        try:
            self.client = boto3.client('translate', region_name=region_name)
            # Test credentials by making a simple call
            self.client.list_languages()
        except NoCredentialsError:
            raise ValueError(
                "AWS credentials not configured. Set up credentials via:\n"
                "  - AWS CLI: aws configure\n"
                "  - Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY\n"
                "  - IAM role (if running on EC2/Lambda)"
            )
    
    def translate(self, text: str, source_language: str, target_language: str) -> str:
        """Translate text using AWS Translate."""
        if not text.strip():
            return text
        
        response = self.client.translate_text(
            Text=text,
            SourceLanguageCode=source_language,
            TargetLanguageCode=target_language
        )
        
        return response['TranslatedText']
    
    def detect_language(self, text: str) -> str:
        """Detect language using AWS Comprehend."""
        try:
            import boto3
        except ImportError:
            raise ImportError("boto3 is required for language detection")
        
        comprehend = boto3.client('comprehend', region_name='us-east-1')
        response = comprehend.detect_dominant_language(Text=text[:5000])  # Max 5000 chars
        
        if response['Languages']:
            return response['Languages'][0]['LanguageCode']
        
        return 'unknown'
    
    def estimate_cost(self, char_count: int) -> float:
        """
        Estimate AWS Translate cost.
        
        AWS Translate pricing (as of 2024):
        - $15 per million characters
        """
        return (char_count / 1_000_000) * 15.0


def normalize_language_code(code: str) -> str:
    """
    Normalize language code to 2-letter ISO 639-1 format.
    
    Args:
        code: Language code (e.g., 'eng', 'en-US', 'english')
        
    Returns:
        Normalized 2-letter code (e.g., 'en')
    """
    code = code.lower().strip()
    
    # Handle common formats
    if '-' in code:
        code = code.split('-')[0]
    
    # Map 3-letter to 2-letter codes
    mapping = {
        'eng': 'en',
        'spa': 'es',
        'fra': 'fr',
        'deu': 'de',
        'ita': 'it',
        'por': 'pt',
        'rus': 'ru',
        'jpn': 'ja',
        'kor': 'ko',
        'zho': 'zh',
        'ara': 'ar',
    }
    
    return mapping.get(code, code)


def check_tiktok_subtitles(post: Dict, target_language: str) -> Optional[Dict]:
    """
    Check if TikTok already has subtitles in target language.
    
    Args:
        post: Post object from TikAPI
        target_language: Target language code
        
    Returns:
        Subtitle info dict or None if not found
    """
    if 'video' not in post or 'subtitleInfos' not in post['video']:
        return None
    
    subtitles = post['video']['subtitleInfos']
    normalized_target = normalize_language_code(target_language)
    
    # Look for subtitle in target language (prefer ASR over MT)
    for subtitle in subtitles:
        lang_code = subtitle.get('LanguageCodeName', '')
        normalized_code = normalize_language_code(lang_code.split('-')[0])
        
        if normalized_code == normalized_target:
            return subtitle
    
    return None


def translate_transcripts(
    transcripts_file: Path,
    target_languages: List[str],
    service: str = "aws",
    output_dir: Optional[Path] = None,
    update_mode: bool = False,
    estimate_only: bool = False,
    source_language: Optional[str] = None
) -> Dict:
    """
    Translate transcripts to target languages.
    
    Checks TikTok's native subtitles first before using translation service.
    
    Args:
        transcripts_file: Path to transcripts JSON file
        target_languages: List of target language codes (e.g., ['en', 'es'])
        service: Translation service to use ('aws' supported, more coming)
        output_dir: Directory to save translations (defaults to transcripts_file.parent)
        update_mode: Only translate new transcripts
        estimate_only: Only estimate costs without translating
        source_language: Source language code (auto-detected if None)
        
    Returns:
        Dictionary with translation results
        
    Example:
        >>> results = translate_transcripts(
        ...     Path("data/user/transcripts/user_transcripts.json"),
        ...     target_languages=['en'],
        ...     service='aws'
        ... )
        >>> print(f"Translated {results['translations_created']} transcripts")
    """
    if not transcripts_file.exists():
        raise FileNotFoundError(f"Transcripts file not found: {transcripts_file}")
    
    # Load transcripts
    print(f"Loading transcripts from {transcripts_file}...")
    with open(transcripts_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    username = data.get('username', 'unknown')
    transcripts = data.get('transcripts', [])
    
    print(f"Found {len(transcripts)} transcripts for @{username}")
    print(f"Target languages: {', '.join(target_languages)}")
    
    # Normalize language codes
    target_languages = [normalize_language_code(lang) for lang in target_languages]
    
    # Set up output directory
    if output_dir is None:
        output_dir = transcripts_file.parent
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Initialize translation service
    translation_service = None
    if not estimate_only:
        if service == "aws":
            print(f"\nInitializing AWS Translate service...")
            translation_service = AWSTranslateService()
        else:
            raise ValueError(
                f"Unsupported translation service: {service}. "
                f"Currently supported: aws"
            )
    
    # Load existing translations if in update mode
    existing_translations = {}
    translations_json_path = output_dir / f"{username}_translations.json"
    
    if update_mode and translations_json_path.exists():
        print(f"\nUpdate mode: Loading existing translations...")
        try:
            with open(translations_json_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                for trans in existing_data.get('translations', []):
                    key = (trans['post_id'], trans['target_language'])
                    existing_translations[key] = trans
                print(f"  Found {len(existing_translations)} existing translations")
        except Exception as e:
            print(f"  Warning: Could not load existing translations: {e}")
    
    results = {
        'total_transcripts': len(transcripts),
        'translations_created': 0,
        'tiktok_subtitles_used': 0,
        'service_translated': 0,
        'failed': 0,
        'skipped_existing': 0,
        'total_characters': 0,
        'estimated_cost': 0.0,
        'translations': []
    }
    
    # Calculate total characters for cost estimate
    for transcript_data in transcripts:
        transcript_text = transcript_data.get('transcript', '')
        results['total_characters'] += len(transcript_text) * len(target_languages)
    
    # Estimate costs
    if translation_service:
        estimated_cost = translation_service.estimate_cost(results['total_characters'])
        results['estimated_cost'] = estimated_cost
        print(f"\nEstimated translation cost: ${estimated_cost:.4f} USD")
        print(f"  ({results['total_characters']:,} characters × {len(target_languages)} languages)")
    
    if estimate_only:
        print("\nEstimate-only mode: Not performing translations")
        return results
    
    # Load posts data to check for TikTok subtitles
    posts_file = transcripts_file.parent.parent / f"{username}_posts.json"
    posts_by_id = {}
    
    if posts_file.exists():
        print(f"\nLoading posts data to check for native TikTok subtitles...")
        with open(posts_file, 'r', encoding='utf-8') as f:
            posts_data = json.load(f)
            posts_by_id = {p['id']: p for p in posts_data.get('posts', [])}
        print(f"  Loaded {len(posts_by_id)} posts")
    
    # Process each transcript
    for i, transcript_data in enumerate(transcripts, 1):
        post_id = transcript_data.get('post_id')
        transcript_text = transcript_data.get('transcript', '')
        original_language = normalize_language_code(
            transcript_data.get('language', source_language or 'unknown').split('-')[0]
        )
        
        print(f"\n[{i}/{len(transcripts)}] Post {post_id}")
        print(f"  Original language: {original_language}")
        print(f"  Text length: {len(transcript_text)} characters")
        
        if not transcript_text.strip():
            print(f"  X Empty transcript, skipping")
            results['failed'] += 1
            continue
        
        # Translate to each target language
        for target_lang in target_languages:
            print(f"\n  Target language: {target_lang}")
            
            # Skip if already translated
            if update_mode and (post_id, target_lang) in existing_translations:
                print(f"    Already translated, skipping...")
                results['skipped_existing'] += 1
                results['translations'].append(existing_translations[(post_id, target_lang)])
                continue
            
            # Skip if same as original language
            if target_lang == original_language:
                print(f"    Same as original language, skipping...")
                continue
            
            # Check if TikTok has native subtitles in target language
            tiktok_subtitle = None
            if post_id in posts_by_id:
                tiktok_subtitle = check_tiktok_subtitles(posts_by_id[post_id], target_lang)
            
            if tiktok_subtitle:
                print(f"    Found TikTok subtitle in {target_lang} - extracting instead of translating")
                # TODO: Download and parse TikTok subtitle
                # For now, we'll proceed with translation
                # results['tiktok_subtitles_used'] += 1
            
            # Translate using service
            try:
                print(f"    Translating with {service}...")
                translated_text = translation_service.translate(
                    transcript_text,
                    original_language,
                    target_lang
                )
                
                results['service_translated'] += 1
                results['translations_created'] += 1
                
                # Save individual translation file
                translation_file = output_dir / f"{post_id}.{target_lang}.txt"
                with open(translation_file, 'w', encoding='utf-8') as f:
                    f.write(f"Post ID: {post_id}\n")
                    f.write(f"Description: {transcript_data.get('description', '')}\n")
                    f.write(f"Original Language: {original_language}\n")
                    f.write(f"Target Language: {target_lang}\n")
                    f.write(f"Translation Service: {service}\n")
                    f.write(f"\n{translated_text}\n")
                
                # Store translation data
                translation_data = {
                    'post_id': post_id,
                    'description': transcript_data.get('description', ''),
                    'create_time': transcript_data.get('create_time', 0),
                    'source_language': original_language,
                    'target_language': target_lang,
                    'translation_service': service,
                    'is_native_subtitle': False,
                    'original_text': transcript_text,
                    'translated_text': translated_text,
                    'character_count': len(transcript_text),
                    'stats': transcript_data.get('stats', {})
                }
                
                results['translations'].append(translation_data)
                
                print(f"    Saved translation ({len(translated_text)} chars)")
                
            except Exception as e:
                print(f"    X Translation failed: {e}")
                results['failed'] += 1
                continue
    
    # Save JSON with all translation data
    with open(translations_json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'username': username,
            'target_languages': target_languages,
            'translation_service': service,
            'summary': {
                'total_transcripts': results['total_transcripts'],
                'translations_created': results['translations_created'],
                'service_translated': results['service_translated'],
                'tiktok_subtitles_used': results['tiktok_subtitles_used'],
                'failed': results['failed'],
                'estimated_cost': results['estimated_cost']
            },
            'translations': results['translations']
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n\nSaved translation data to {translations_json_path}")
    print(f"\nSummary:")
    print(f"  Total transcripts: {results['total_transcripts']}")
    print(f"  Translations created: {results['translations_created']}")
    print(f"  Service translated: {results['service_translated']}")
    print(f"  TikTok subtitles used: {results['tiktok_subtitles_used']}")
    print(f"  Failed: {results['failed']}")
    print(f"  Skipped (existing): {results['skipped_existing']}")
    if results['estimated_cost'] > 0:
        print(f"  Estimated cost: ${results['estimated_cost']:.4f} USD")
    
    return results

