"""
Telegram Bot API Handler - Telegram data collection using Bot API
Uses the Bot API (simpler, works with bot token from @BotFather)
"""
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import asdict

from ..entities.post import TelegramMessage
from ..utils.hashing import hash_username
from ..utils.rate_limiter import RateLimiter, RateLimitConfig
from ..utils.file_manager import FileManager
from ..core.analyzer import TextAnalyzer


class TelegramBotHandler:
    """
    Handles Telegram data collection using Bot API
    Simpler alternative to Telethon - works with bot token from @BotFather
    """
    
    BASE_URL = "https://api.telegram.org/bot"
    
    def __init__(
        self,
        bot_token: str,
        data_dir: str = "collected_data"
    ):
        """
        Initialize Telegram Bot handler
        
        Args:
            bot_token: Bot token from @BotFather (format: 123456:ABC-DEF...)
            data_dir: Directory for storing collected data
        """
        self.bot_token = bot_token
        self.api_url = f"{self.BASE_URL}{bot_token}"
        
        self.rate_limiter = RateLimiter(RateLimitConfig(
            requests_per_second=1,
            requests_per_minute=30
        ))
        self.file_manager = FileManager(data_dir)
        self.analyzer = TextAnalyzer()
        
        self.disclaimer = """
        ACADEMIC RESEARCH DATA COLLECTION
        This data is collected for legitimate academic research purposes only.
        All data handling follows academic ethics guidelines and privacy laws.
        """
        
        # Verify bot token
        self._bot_info = None
        print(f"TelegramBotHandler initialized")
    
    def verify_token(self) -> Dict[str, Any]:
        """Verify the bot token and get bot info"""
        try:
            response = requests.get(f"{self.api_url}/getMe", timeout=10)
            data = response.json()
            
            if data.get('ok'):
                self._bot_info = data.get('result', {})
                print(f"✓ Bot verified: @{self._bot_info.get('username', 'unknown')}")
                return {
                    'ok': True,
                    'bot_id': self._bot_info.get('id'),
                    'bot_username': self._bot_info.get('username'),
                    'bot_name': self._bot_info.get('first_name')
                }
            else:
                print(f"✗ Bot verification failed: {data.get('description', 'Unknown error')}")
                return {'ok': False, 'error': data.get('description', 'Unknown error')}
                
        except Exception as e:
            print(f"✗ Bot verification error: {str(e)}")
            return {'ok': False, 'error': str(e)}
    
    def get_updates(self, offset: int = 0, limit: int = 100) -> List[Dict]:
        """
        Get recent updates/messages the bot has received
        
        Note: Bot API only returns messages where the bot is mentioned
        or messages in groups where the bot has access
        
        Args:
            offset: Identifier of the first update to return
            limit: Maximum number of updates (1-100)
            
        Returns:
            List of update objects
        """
        try:
            self.rate_limiter.acquire()
            
            response = requests.get(
                f"{self.api_url}/getUpdates",
                params={'offset': offset, 'limit': limit, 'timeout': 30},
                timeout=35
            )
            data = response.json()
            
            if data.get('ok'):
                updates = data.get('result', [])
                print(f"Retrieved {len(updates)} updates")
                return updates
            else:
                print(f"Error getting updates: {data.get('description')}")
                return []
                
        except Exception as e:
            print(f"Error getting updates: {str(e)}")
            return []
    
    def get_chat_info(self, chat_id: str) -> Optional[Dict]:
        """
        Get information about a chat/channel/group
        
        Args:
            chat_id: Chat ID or @username
            
        Returns:
            Chat info dict or None
        """
        try:
            self.rate_limiter.acquire()
            
            response = requests.get(
                f"{self.api_url}/getChat",
                params={'chat_id': chat_id},
                timeout=10
            )
            data = response.json()
            
            if data.get('ok'):
                return data.get('result')
            else:
                print(f"Error getting chat info: {data.get('description')}")
                return None
                
        except Exception as e:
            print(f"Error getting chat info: {str(e)}")
            return None
    
    def forward_channel_message(
        self,
        from_chat_id: str,
        message_id: int,
        to_chat_id: str
    ) -> Optional[Dict]:
        """
        Forward a message from a channel (requires bot to be admin in channel)
        
        Args:
            from_chat_id: Source channel/chat ID
            message_id: Message ID to forward
            to_chat_id: Destination chat ID
            
        Returns:
            Forwarded message or None
        """
        try:
            self.rate_limiter.acquire()
            
            response = requests.post(
                f"{self.api_url}/forwardMessage",
                json={
                    'chat_id': to_chat_id,
                    'from_chat_id': from_chat_id,
                    'message_id': message_id
                },
                timeout=10
            )
            data = response.json()
            
            if data.get('ok'):
                return data.get('result')
            return None
            
        except Exception as e:
            print(f"Error forwarding message: {str(e)}")
            return None
    
    def collect_from_updates(self, limit: int = 100) -> List[TelegramMessage]:
        """
        Collect messages from bot updates
        
        This collects messages that the bot has received, including:
        - Direct messages to the bot
        - Messages in groups where bot is a member
        - Channel posts where bot is admin
        
        Args:
            limit: Maximum updates to process
            
        Returns:
            List of TelegramMessage objects
        """
        updates = self.get_updates(limit=limit)
        
        collected_messages = []
        
        for update in updates:
            message = update.get('message') or update.get('channel_post')
            
            if not message:
                continue
            
            text = message.get('text', '')
            if not text:
                continue
            
            chat = message.get('chat', {})
            sender = message.get('from', {})
            
            # Hash sender for privacy
            sender_id = str(sender.get('id', 'anonymous'))
            author_hash = hash_username(sender_id)
            
            # Determine chat type
            chat_type = chat.get('type', 'unknown')
            chat_title = chat.get('title') or chat.get('username') or str(chat.get('id', ''))
            
            # Build URL
            chat_username = chat.get('username')
            if chat_username:
                url = f"https://t.me/{chat_username}/{message.get('message_id', '')}"
            else:
                url = ""
            
            telegram_msg = TelegramMessage(
                id=str(message.get('message_id', update.get('update_id'))),
                content=text,
                author_hash=author_hash,
                chat_id=chat.get('id', 0),
                chat_title=chat_title,
                chat_type=chat_type,
                created_at=message.get('date', 0),
                views=None,  # Not available in Bot API
                forwards=None,
                replies=None,
                media_type=self._get_media_type(message),
                url=url,
                collected_at=datetime.now().isoformat(),
                platform="telegram"
            )
            
            collected_messages.append(telegram_msg)
        
        print(f"Collected {len(collected_messages)} messages from updates")
        return collected_messages
    
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
                "method": "bot_api",
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
    
    def _get_media_type(self, message: Dict) -> Optional[str]:
        """Determine media type from message"""
        if message.get('photo'):
            return 'photo'
        elif message.get('video'):
            return 'video'
        elif message.get('document'):
            return 'document'
        elif message.get('audio'):
            return 'audio'
        elif message.get('voice'):
            return 'voice'
        elif message.get('sticker'):
            return 'sticker'
        return None
    
    def send_message(self, chat_id: str, text: str) -> Optional[Dict]:
        """
        Send a message (useful for testing bot functionality)
        
        Args:
            chat_id: Target chat ID
            text: Message text
            
        Returns:
            Sent message or None
        """
        try:
            self.rate_limiter.acquire()
            
            response = requests.post(
                f"{self.api_url}/sendMessage",
                json={
                    'chat_id': chat_id,
                    'text': text
                },
                timeout=10
            )
            data = response.json()
            
            if data.get('ok'):
                return data.get('result')
            return None
            
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return None

