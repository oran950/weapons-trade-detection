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
    
    def __post_init__(self):
        self.platform = "reddit"
    
    @classmethod
    def from_praw_submission(cls, submission, author_hash: str) -> 'RedditPost':
        """Create a RedditPost from a PRAW submission object"""
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
            platform="reddit"
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

