"""
Post entities for different platforms (Reddit, Telegram)
"""
from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any, List
from datetime import datetime


@dataclass
class Post:
    """Base class for all platform posts"""
    id: str
    content: str
    author_hash: str  # Hashed for privacy
    created_at: float
    url: str
    collected_at: str
    platform: str
    risk_analysis: Optional[Dict] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RedditPost(Post):
    """Data structure for collected Reddit posts"""
    title: str = ""
    subreddit: str = ""
    score: int = 0
    num_comments: int = 0
    image_url: Optional[str] = None  # Main image URL
    thumbnail: Optional[str] = None  # Thumbnail URL
    media_type: Optional[str] = None  # 'image', 'video', 'gallery', 'link', 'text'
    gallery_images: Optional[List[str]] = None  # Multiple images for gallery posts
    is_video: bool = False
    video_url: Optional[str] = None
    
    def __post_init__(self):
        self.platform = "reddit"
    
    @classmethod
    def from_praw_submission(cls, submission, author_hash: str) -> 'RedditPost':
        """Create a RedditPost from a PRAW submission object"""
        # Extract image/media information
        image_url = None
        thumbnail = None
        media_type = 'text'
        gallery_images = None
        is_video = False
        video_url = None
        
        # Check for direct image
        if hasattr(submission, 'url'):
            url = submission.url
            if any(url.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                image_url = url
                media_type = 'image'
            elif 'i.redd.it' in url or 'i.imgur.com' in url:
                image_url = url
                media_type = 'image'
            elif 'v.redd.it' in url:
                is_video = True
                video_url = url
                media_type = 'video'
            elif url != f"https://www.reddit.com{submission.permalink}":
                media_type = 'link'
        
        # Check for gallery posts
        if hasattr(submission, 'is_gallery') and submission.is_gallery:
            media_type = 'gallery'
            gallery_images = []
            if hasattr(submission, 'media_metadata') and submission.media_metadata:
                for item_id, item in submission.media_metadata.items():
                    if item.get('status') == 'valid' and 's' in item:
                        img_url = item['s'].get('u', '').replace('&amp;', '&')
                        if img_url:
                            gallery_images.append(img_url)
                if gallery_images:
                    image_url = gallery_images[0]  # First image as main
        
        # Check for preview images
        if not image_url and hasattr(submission, 'preview'):
            try:
                previews = submission.preview.get('images', [])
                if previews:
                    image_url = previews[0]['source']['url'].replace('&amp;', '&')
                    if media_type == 'text':
                        media_type = 'image'
            except (KeyError, IndexError, TypeError):
                pass
        
        # Get thumbnail
        if hasattr(submission, 'thumbnail') and submission.thumbnail not in ['self', 'default', 'nsfw', 'spoiler', '']:
            thumbnail = submission.thumbnail
            # Use thumbnail as fallback for image_url if no other image found
            if not image_url and thumbnail.startswith('http'):
                image_url = thumbnail
                if media_type == 'text' or media_type == 'link':
                    media_type = 'image'
        
        # Check if video
        if hasattr(submission, 'is_video') and submission.is_video:
            is_video = True
            media_type = 'video'
            if hasattr(submission, 'media') and submission.media:
                if 'reddit_video' in submission.media:
                    video_url = submission.media['reddit_video'].get('fallback_url')
        
        return cls(
            id=submission.id,
            title=submission.title,
            content=submission.selftext if hasattr(submission, 'selftext') else "",
            subreddit=str(submission.subreddit),
            author_hash=author_hash,
            score=submission.score,
            num_comments=submission.num_comments,
            created_at=submission.created_utc,
            url=f"https://reddit.com{submission.permalink}",
            collected_at=datetime.now().isoformat(),
            platform="reddit",
            image_url=image_url,
            thumbnail=thumbnail,
            media_type=media_type,
            gallery_images=gallery_images,
            is_video=is_video,
            video_url=video_url
        )


@dataclass
class TelegramMessage(Post):
    """Data structure for collected Telegram messages"""
    chat_id: int = 0
    chat_title: str = ""
    chat_type: str = ""  # 'channel', 'group', 'supergroup'
    views: Optional[int] = None
    forwards: Optional[int] = None
    replies: Optional[int] = None
    media_type: Optional[str] = None  # 'photo', 'video', 'document', None
    
    def __post_init__(self):
        self.platform = "telegram"
    
    @classmethod
    def from_telethon_message(cls, message, author_hash: str, chat_info: Dict) -> 'TelegramMessage':
        """Create a TelegramMessage from a Telethon message object"""
        media_type = None
        if message.media:
            if hasattr(message.media, 'photo'):
                media_type = 'photo'
            elif hasattr(message.media, 'video'):
                media_type = 'video'
            elif hasattr(message.media, 'document'):
                media_type = 'document'
        
        return cls(
            id=str(message.id),
            content=message.text or "",
            author_hash=author_hash,
            chat_id=message.chat_id,
            chat_title=chat_info.get('title', ''),
            chat_type=chat_info.get('type', 'unknown'),
            created_at=message.date.timestamp(),
            views=getattr(message, 'views', None),
            forwards=getattr(message, 'forwards', None),
            replies=getattr(message.replies, 'replies', None) if message.replies else None,
            media_type=media_type,
            url=f"https://t.me/c/{message.chat_id}/{message.id}",
            collected_at=datetime.now().isoformat(),
            platform="telegram"
        )

