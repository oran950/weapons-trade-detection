"""
Telegram Handler - Telegram data collection and processing
Uses Telethon library for async Telegram API access
"""
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import asdict

from ..entities.post import TelegramMessage
from ..entities.analysis import AnalysisResult
from ..utils.hashing import hash_username
from ..utils.rate_limiter import RateLimiter, RateLimitConfig
from ..utils.file_manager import FileManager
from ..core.analyzer import TextAnalyzer


class TelegramHandler:
    """
    Handles Telegram data collection and processing
    Uses Telethon for async API access
    """
    
    def __init__(
        self,
        api_id: int,
        api_hash: str,
        session_name: str = "weapons_detection_session",
        data_dir: str = "collected_data"
    ):
        """
        Initialize Telegram handler with credentials
        
        Args:
            api_id: Telegram API ID (from my.telegram.org)
            api_hash: Telegram API hash (from my.telegram.org)
            session_name: Name for the session file
            data_dir: Directory for storing collected data
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.client = None
        
        self.rate_limiter = RateLimiter(RateLimitConfig(
            requests_per_second=0.5,  # Telegram has stricter limits
            requests_per_minute=30
        ))
        self.file_manager = FileManager(data_dir)
        self.analyzer = TextAnalyzer()
        
        self.disclaimer = """
        ACADEMIC RESEARCH DATA COLLECTION
        This data is collected for legitimate academic research purposes only.
        All data handling follows academic ethics guidelines and privacy laws.
        """
        
        print("TelegramHandler initialized (client not connected)")
    
    async def connect(self) -> bool:
        """
        Connect to Telegram API
        
        Returns:
            True if connection successful
        """
        try:
            from telethon import TelegramClient
            
            self.client = TelegramClient(
                self.session_name,
                self.api_id,
                self.api_hash
            )
            
            await self.client.start()
            print("TelegramHandler connected successfully")
            return True
            
        except ImportError:
            print("Telethon library required. Install with: pip install telethon")
            return False
        except Exception as e:
            print(f"Failed to connect to Telegram: {str(e)}")
            return False
    
    async def disconnect(self):
        """Disconnect from Telegram API"""
        if self.client:
            await self.client.disconnect()
            print("TelegramHandler disconnected")
    
    async def collect_channel_messages(
        self,
        channel_username: str,
        limit: int = 100,
        offset_date: Optional[datetime] = None
    ) -> List[TelegramMessage]:
        """
        Collect messages from a public Telegram channel
        
        Args:
            channel_username: Channel username (without @)
            limit: Maximum number of messages to collect
            offset_date: Only get messages before this date
            
        Returns:
            List of TelegramMessage objects
        """
        if not self.client:
            print("Client not connected. Call connect() first.")
            return []
        
        print(f"Collecting from @{channel_username} (limit: {limit})")
        
        try:
            from telethon.tl.functions.messages import GetHistoryRequest
            
            # Get channel entity
            channel = await self.client.get_entity(channel_username)
            
            chat_info = {
                'title': getattr(channel, 'title', channel_username),
                'type': self._get_chat_type(channel)
            }
            
            collected_messages = []
            
            async for message in self.client.iter_messages(
                channel,
                limit=limit,
                offset_date=offset_date
            ):
                await self.rate_limiter.acquire_async()
                
                if not message.text:
                    continue
                
                # Hash sender ID for privacy
                sender_id = str(message.sender_id) if message.sender_id else "anonymous"
                author_hash = hash_username(sender_id)
                
                telegram_msg = TelegramMessage(
                    id=str(message.id),
                    content=message.text or "",
                    author_hash=author_hash,
                    chat_id=message.chat_id,
                    chat_title=chat_info['title'],
                    chat_type=chat_info['type'],
                    created_at=message.date.timestamp(),
                    views=getattr(message, 'views', None),
                    forwards=getattr(message, 'forwards', None),
                    replies=getattr(message.replies, 'replies', None) if message.replies else None,
                    media_type=self._get_media_type(message),
                    url=f"https://t.me/{channel_username}/{message.id}",
                    collected_at=datetime.now().isoformat(),
                    platform="telegram"
                )
                
                collected_messages.append(telegram_msg)
            
            print(f"Collected {len(collected_messages)} messages from @{channel_username}")
            return collected_messages
            
        except Exception as e:
            print(f"Error collecting from @{channel_username}: {str(e)}")
            return []
    
    async def collect_group_messages(
        self,
        group_id: int,
        limit: int = 100
    ) -> List[TelegramMessage]:
        """
        Collect messages from a Telegram group
        
        Args:
            group_id: Group ID
            limit: Maximum number of messages
            
        Returns:
            List of TelegramMessage objects
        """
        if not self.client:
            print("Client not connected")
            return []
        
        try:
            group = await self.client.get_entity(group_id)
            chat_info = {
                'title': getattr(group, 'title', str(group_id)),
                'type': self._get_chat_type(group)
            }
            
            collected_messages = []
            
            async for message in self.client.iter_messages(group, limit=limit):
                await self.rate_limiter.acquire_async()
                
                if not message.text:
                    continue
                
                sender_id = str(message.sender_id) if message.sender_id else "anonymous"
                author_hash = hash_username(sender_id)
                
                telegram_msg = TelegramMessage(
                    id=str(message.id),
                    content=message.text or "",
                    author_hash=author_hash,
                    chat_id=message.chat_id,
                    chat_title=chat_info['title'],
                    chat_type=chat_info['type'],
                    created_at=message.date.timestamp(),
                    views=getattr(message, 'views', None),
                    forwards=getattr(message, 'forwards', None),
                    replies=getattr(message.replies, 'replies', None) if message.replies else None,
                    media_type=self._get_media_type(message),
                    url=f"https://t.me/c/{message.chat_id}/{message.id}",
                    collected_at=datetime.now().isoformat(),
                    platform="telegram"
                )
                
                collected_messages.append(telegram_msg)
            
            return collected_messages
            
        except Exception as e:
            print(f"Error collecting from group {group_id}: {str(e)}")
            return []
    
    async def search_messages(
        self,
        query: str,
        limit: int = 50
    ) -> List[TelegramMessage]:
        """
        Search for messages across all accessible chats
        
        Args:
            query: Search query string
            limit: Maximum results
            
        Returns:
            List of TelegramMessage objects
        """
        if not self.client:
            print("Client not connected")
            return []
        
        print(f"Searching for: '{query}'")
        
        try:
            from telethon.tl.functions.messages import SearchGlobalRequest
            from telethon.tl.types import InputMessagesFilterEmpty
            
            results = await self.client(SearchGlobalRequest(
                q=query,
                filter=InputMessagesFilterEmpty(),
                min_date=None,
                max_date=None,
                offset_rate=0,
                offset_peer=None,
                offset_id=0,
                limit=limit
            ))
            
            collected_messages = []
            
            for message in results.messages:
                if not hasattr(message, 'message') or not message.message:
                    continue
                
                sender_id = str(message.from_id.user_id) if hasattr(message, 'from_id') and message.from_id else "anonymous"
                author_hash = hash_username(sender_id)
                
                telegram_msg = TelegramMessage(
                    id=str(message.id),
                    content=message.message,
                    author_hash=author_hash,
                    chat_id=message.peer_id.channel_id if hasattr(message.peer_id, 'channel_id') else 0,
                    chat_title="search_result",
                    chat_type="search",
                    created_at=message.date.timestamp(),
                    views=getattr(message, 'views', None),
                    forwards=getattr(message, 'forwards', None),
                    replies=None,
                    media_type=None,
                    url="",
                    collected_at=datetime.now().isoformat(),
                    platform="telegram"
                )
                
                collected_messages.append(telegram_msg)
            
            print(f"Found {len(collected_messages)} messages matching '{query}'")
            return collected_messages
            
        except Exception as e:
            print(f"Error searching for '{query}': {str(e)}")
            return []
    
    async def collect_by_keywords(
        self,
        keywords: List[str],
        channels: List[str],
        limit_per_channel: int = 50
    ) -> List[TelegramMessage]:
        """
        Collect messages containing specific keywords from channels
        
        Args:
            keywords: Keywords to search for
            channels: List of channel usernames
            limit_per_channel: Max messages per channel
            
        Returns:
            List of TelegramMessage objects containing keywords
        """
        all_messages = []
        
        for channel in channels:
            messages = await self.collect_channel_messages(channel, limit_per_channel)
            
            # Filter messages containing keywords
            keyword_lower = [k.lower() for k in keywords]
            filtered = [
                m for m in messages 
                if any(kw in m.content.lower() for kw in keyword_lower)
            ]
            
            all_messages.extend(filtered)
        
        return all_messages
    
    def analyze_messages(self, messages: List[TelegramMessage]) -> List[TelegramMessage]:
        """
        Analyze collected messages for weapons trade indicators
        
        Args:
            messages: List of TelegramMessage objects
            
        Returns:
            List of TelegramMessage objects with risk_analysis
        """
        print(f"Analyzing {len(messages)} messages...")
        
        analyzed_messages = []
        
        for msg in messages:
            if not msg.content:
                continue
            
            try:
                analysis = self.analyzer.analyze_text(msg.content)
                msg.risk_analysis = analysis.to_dict()
                analyzed_messages.append(msg)
                
                if analysis.risk_score >= 0.7:
                    print(f"HIGH RISK: {msg.chat_title}/{msg.id} - Score: {analysis.risk_score:.2f}")
                    
            except Exception as e:
                print(f"Error analyzing message {msg.id}: {str(e)}")
                continue
        
        return analyzed_messages
    
    def save_messages(
        self,
        messages: List[TelegramMessage],
        filename: str,
        include_csv: bool = True
    ) -> List[str]:
        """
        Save messages to files
        
        Args:
            messages: List of messages to save
            filename: Base filename
            include_csv: Whether to also save as CSV
            
        Returns:
            List of saved file paths
        """
        saved_files = []
        
        messages_data = [asdict(msg) for msg in messages]
        
        json_data = {
            "collection_info": {
                "collected_at": datetime.now().isoformat(),
                "total_messages": len(messages),
                "platform": "telegram",
                "disclaimer": self.disclaimer.strip()
            },
            "messages": messages_data
        }
        
        json_path = self.file_manager.save_json(json_data, filename, "raw")
        saved_files.append(json_path)
        
        if include_csv:
            csv_path = self.file_manager.save_csv(messages_data, filename, "raw")
            saved_files.append(csv_path)
        
        return saved_files
    
    def _get_chat_type(self, entity) -> str:
        """Determine chat type from entity"""
        entity_type = type(entity).__name__
        
        if 'Channel' in entity_type:
            if getattr(entity, 'megagroup', False):
                return 'supergroup'
            return 'channel'
        elif 'Chat' in entity_type:
            return 'group'
        return 'unknown'
    
    def _get_media_type(self, message) -> Optional[str]:
        """Determine media type from message"""
        if not message.media:
            return None
        
        media_type = type(message.media).__name__
        
        if 'Photo' in media_type:
            return 'photo'
        elif 'Document' in media_type:
            if hasattr(message.media, 'attributes'):
                for attr in message.media.attributes:
                    if 'Video' in type(attr).__name__:
                        return 'video'
            return 'document'
        elif 'Video' in media_type:
            return 'video'
        
        return 'other'

