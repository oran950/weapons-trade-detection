"""
Collection Workflow - Orchestrates data collection across platforms
"""
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field

from ..entities.post import RedditPost, TelegramMessage
from ..handlers.reddit_handler import RedditHandler
from ..handlers.telegram_handler import TelegramHandler
from ..utils.file_manager import FileManager
from ..config import config


@dataclass
class CollectionConfig:
    """Configuration for collection workflow"""
    # Reddit settings
    reddit_subreddits: List[str] = field(default_factory=list)
    reddit_time_filter: str = "day"
    reddit_sort_method: str = "hot"
    reddit_limit_per_subreddit: int = 25
    reddit_keywords: List[str] = field(default_factory=list)
    
    # Telegram settings
    telegram_channels: List[str] = field(default_factory=list)
    telegram_groups: List[int] = field(default_factory=list)
    telegram_keywords: List[str] = field(default_factory=list)
    telegram_limit_per_source: int = 50
    
    # General settings
    enable_reddit: bool = True
    enable_telegram: bool = False
    analyze_after_collection: bool = True


class CollectionWorkflow:
    """
    Orchestrates data collection across Reddit and Telegram
    """
    
    def __init__(self, workflow_config: Optional[CollectionConfig] = None):
        """
        Initialize collection workflow
        
        Args:
            workflow_config: Collection configuration
        """
        self.config = workflow_config or CollectionConfig()
        self.file_manager = FileManager(config.DATA_DIR)
        
        self.reddit_handler: Optional[RedditHandler] = None
        self.telegram_handler: Optional[TelegramHandler] = None
        
        self._init_handlers()
    
    def _init_handlers(self):
        """Initialize platform handlers"""
        # Reddit
        if self.config.enable_reddit and config.reddit_configured:
            try:
                self.reddit_handler = RedditHandler(
                    client_id=config.REDDIT_CLIENT_ID,
                    client_secret=config.REDDIT_CLIENT_SECRET,
                    user_agent=config.REDDIT_USER_AGENT,
                    data_dir=config.DATA_DIR
                )
            except Exception as e:
                print(f"Failed to initialize Reddit handler: {e}")
        
        # Telegram (async initialization needed)
        if self.config.enable_telegram and config.telegram_configured:
            self.telegram_handler = TelegramHandler(
                api_id=config.TELEGRAM_API_ID,
                api_hash=config.TELEGRAM_API_HASH,
                data_dir=config.DATA_DIR
            )
    
    async def run(self) -> Dict[str, Any]:
        """
        Run the collection workflow
        
        Returns:
            Dictionary with collection results
        """
        results = {
            "workflow_id": f"collection_{int(datetime.now().timestamp())}",
            "started_at": datetime.now().isoformat(),
            "reddit_posts": [],
            "telegram_messages": [],
            "summary": {},
            "errors": []
        }
        
        # Collect from Reddit
        if self.config.enable_reddit and self.reddit_handler:
            try:
                reddit_posts = await self._collect_reddit()
                results["reddit_posts"] = reddit_posts
            except Exception as e:
                results["errors"].append(f"Reddit collection failed: {e}")
        
        # Collect from Telegram
        if self.config.enable_telegram and self.telegram_handler:
            try:
                telegram_messages = await self._collect_telegram()
                results["telegram_messages"] = telegram_messages
            except Exception as e:
                results["errors"].append(f"Telegram collection failed: {e}")
        
        # Generate summary
        results["summary"] = {
            "reddit_count": len(results["reddit_posts"]),
            "telegram_count": len(results["telegram_messages"]),
            "total_count": len(results["reddit_posts"]) + len(results["telegram_messages"]),
            "errors_count": len(results["errors"])
        }
        
        results["completed_at"] = datetime.now().isoformat()
        
        return results
    
    async def _collect_reddit(self) -> List[RedditPost]:
        """Collect from Reddit (runs in thread pool)"""
        if not self.reddit_handler:
            return []
        
        loop = asyncio.get_event_loop()
        all_posts = []
        
        for subreddit in self.config.reddit_subreddits:
            if self.config.reddit_keywords:
                posts = await loop.run_in_executor(
                    None,
                    lambda s=subreddit: self.reddit_handler.search_posts_by_keywords(
                        s,
                        self.config.reddit_keywords,
                        self.config.reddit_time_filter,
                        self.config.reddit_limit_per_subreddit
                    )
                )
            else:
                posts = await loop.run_in_executor(
                    None,
                    lambda s=subreddit: self.reddit_handler.collect_subreddit_posts(
                        s,
                        self.config.reddit_time_filter,
                        self.config.reddit_limit_per_subreddit,
                        self.config.reddit_sort_method
                    )
                )
            all_posts.extend(posts)
        
        # Analyze if configured
        if self.config.analyze_after_collection:
            all_posts = self.reddit_handler.analyze_posts(all_posts)
        
        return all_posts
    
    async def _collect_telegram(self) -> List[TelegramMessage]:
        """Collect from Telegram"""
        if not self.telegram_handler:
            return []
        
        if not await self.telegram_handler.connect():
            raise RuntimeError("Failed to connect to Telegram")
        
        all_messages = []
        
        try:
            # Collect from channels
            for channel in self.config.telegram_channels:
                messages = await self.telegram_handler.collect_channel_messages(
                    channel,
                    self.config.telegram_limit_per_source
                )
                all_messages.extend(messages)
            
            # Collect from groups
            for group_id in self.config.telegram_groups:
                messages = await self.telegram_handler.collect_group_messages(
                    group_id,
                    self.config.telegram_limit_per_source
                )
                all_messages.extend(messages)
            
            # Analyze if configured
            if self.config.analyze_after_collection:
                all_messages = self.telegram_handler.analyze_messages(all_messages)
                
        finally:
            await self.telegram_handler.disconnect()
        
        return all_messages
    
    def save_results(
        self, 
        results: Dict[str, Any], 
        filename_prefix: str = None
    ) -> List[str]:
        """
        Save collection results to files
        
        Args:
            results: Collection results
            filename_prefix: Prefix for filenames
            
        Returns:
            List of saved file paths
        """
        saved_files = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        prefix = filename_prefix or f"workflow_{timestamp}"
        
        # Save Reddit posts
        if results["reddit_posts"]:
            from dataclasses import asdict
            reddit_data = {
                "collection_info": {
                    "workflow_id": results["workflow_id"],
                    "collected_at": results["completed_at"],
                    "platform": "reddit",
                    "count": len(results["reddit_posts"])
                },
                "posts": [asdict(p) for p in results["reddit_posts"]]
            }
            path = self.file_manager.save_json(reddit_data, f"{prefix}_reddit", "raw")
            saved_files.append(path)
        
        # Save Telegram messages
        if results["telegram_messages"]:
            from dataclasses import asdict
            telegram_data = {
                "collection_info": {
                    "workflow_id": results["workflow_id"],
                    "collected_at": results["completed_at"],
                    "platform": "telegram",
                    "count": len(results["telegram_messages"])
                },
                "messages": [asdict(m) for m in results["telegram_messages"]]
            }
            path = self.file_manager.save_json(telegram_data, f"{prefix}_telegram", "raw")
            saved_files.append(path)
        
        # Save summary
        summary_data = {
            "workflow_id": results["workflow_id"],
            "started_at": results["started_at"],
            "completed_at": results["completed_at"],
            "summary": results["summary"],
            "errors": results["errors"],
            "saved_files": saved_files
        }
        path = self.file_manager.save_json(summary_data, f"{prefix}_summary", "reports")
        saved_files.append(path)
        
        return saved_files

