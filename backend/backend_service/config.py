"""
Configuration management for the backend service
"""
import os
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """
    Centralized configuration for the backend service
    """
    
    # FastAPI settings
    HOST: str = os.getenv('HOST', '0.0.0.0')
    PORT: int = int(os.getenv('PORT', '9000'))
    DEBUG: bool = os.getenv('DEBUG', 'true').lower() == 'true'
    
    # Data storage
    DATA_DIR: str = os.getenv('DATA_DIR', 'collected_data')
    
    # Reddit API Configuration
    REDDIT_CLIENT_ID: Optional[str] = os.getenv('REDDIT_CLIENT_ID')
    REDDIT_CLIENT_SECRET: Optional[str] = os.getenv('REDDIT_CLIENT_SECRET')
    REDDIT_USER_AGENT: Optional[str] = os.getenv('REDDIT_USER_AGENT')
    REDDIT_RATE_LIMIT_DELAY: int = int(os.getenv('REDDIT_RATE_LIMIT_DELAY', '2'))
    REDDIT_MAX_POSTS_PER_REQUEST: int = int(os.getenv('REDDIT_MAX_POSTS_PER_REQUEST', '50'))
    
    # Telegram API Configuration
    TELEGRAM_API_ID: Optional[int] = None
    TELEGRAM_API_HASH: Optional[str] = os.getenv('TELEGRAM_API_HASH')
    TELEGRAM_SESSION_NAME: str = os.getenv('TELEGRAM_SESSION_NAME', 'weapons_detection_session')
    
    # LLM Configuration
    LLM_PROVIDER: str = os.getenv('LLM_PROVIDER', 'ollama').lower()
    OLLAMA_BASE: str = os.getenv('OLLAMA_BASE', 'http://localhost:11434')
    OLLAMA_MODEL: str = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')
    LLM_TIMEOUT: int = int(os.getenv('LLM_TIMEOUT', '120'))
    
    def __init__(self):
        # Parse Telegram API ID (needs to be int)
        telegram_id = os.getenv('TELEGRAM_API_ID')
        if telegram_id:
            try:
                self.TELEGRAM_API_ID = int(telegram_id)
            except ValueError:
                self.TELEGRAM_API_ID = None
    
    @property
    def reddit_configured(self) -> bool:
        """Check if Reddit API is properly configured"""
        return all([
            self.REDDIT_CLIENT_ID,
            self.REDDIT_CLIENT_SECRET,
            self.REDDIT_USER_AGENT
        ])
    
    @property
    def telegram_configured(self) -> bool:
        """Check if Telegram API is properly configured"""
        return all([
            self.TELEGRAM_API_ID,
            self.TELEGRAM_API_HASH
        ])
    
    @property
    def llm_configured(self) -> bool:
        """Check if LLM is configured"""
        return self.LLM_PROVIDER == 'ollama' and bool(self.OLLAMA_BASE)
    
    def get_missing_reddit_config(self) -> List[str]:
        """Get list of missing Reddit configuration items"""
        missing = []
        if not self.REDDIT_CLIENT_ID:
            missing.append('REDDIT_CLIENT_ID')
        if not self.REDDIT_CLIENT_SECRET:
            missing.append('REDDIT_CLIENT_SECRET')
        if not self.REDDIT_USER_AGENT:
            missing.append('REDDIT_USER_AGENT')
        return missing
    
    def get_missing_telegram_config(self) -> List[str]:
        """Get list of missing Telegram configuration items"""
        missing = []
        if not self.TELEGRAM_API_ID:
            missing.append('TELEGRAM_API_ID')
        if not self.TELEGRAM_API_HASH:
            missing.append('TELEGRAM_API_HASH')
        return missing


# Global config instance
config = Config()

