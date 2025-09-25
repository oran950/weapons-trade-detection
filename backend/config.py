import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

class RedditConfig:
    """Reddit API configuration"""
    
    CLIENT_ID: Optional[str] = os.getenv('REDDIT_CLIENT_ID')
    CLIENT_SECRET: Optional[str] = os.getenv('REDDIT_CLIENT_SECRET')
    USER_AGENT: Optional[str] = os.getenv('REDDIT_USER_AGENT')
    RATE_LIMIT_DELAY: int = int(os.getenv('REDDIT_RATE_LIMIT_DELAY', '2'))
    MAX_POSTS_PER_REQUEST: int = int(os.getenv('REDDIT_MAX_POSTS_PER_REQUEST', '50'))
    
    @classmethod
    def is_configured(cls) -> bool:
        """Check if Reddit API is properly configured"""
        return all([cls.CLIENT_ID, cls.CLIENT_SECRET, cls.USER_AGENT])
    
    @classmethod
    def get_missing_config(cls) -> list:
        """Get list of missing configuration items"""
        missing = []
        if not cls.CLIENT_ID:
            missing.append('REDDIT_CLIENT_ID')
        if not cls.CLIENT_SECRET:
            missing.append('REDDIT_CLIENT_SECRET')
        if not cls.USER_AGENT:
            missing.append('REDDIT_USER_AGENT')
        return missing

class AppConfig:
    """General application configuration"""
    
    # FastAPI settings
    HOST: str = os.getenv('HOST', '0.0.0.0')
    PORT: int = int(os.getenv('PORT', '9000'))
    DEBUG: bool = os.getenv('DEBUG', 'true').lower() == 'true'
    
    # Data storage
    DATA_DIR: str = os.getenv('DATA_DIR', 'collected_data')
    
    # Reddit configuration
    reddit = RedditConfig