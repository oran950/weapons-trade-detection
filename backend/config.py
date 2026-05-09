import os
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Optional, Set

_BACKEND_ROOT = Path(__file__).resolve().parent

# Load environment variables: prefer backend/.env regardless of process cwd.
# override=True so values from this file win over empty/stale vars (e.g. Docker env_file quirks).
load_dotenv(_BACKEND_ROOT / ".env", override=True)
load_dotenv(override=False)

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

class OllamaConfig:
    """Ollama LLM configuration"""
    
    # Prefer OLLAMA_BASE; OLLAMA_HOST is legacy alias used in some .env files
    BASE: str = (os.getenv("OLLAMA_BASE") or os.getenv("OLLAMA_HOST") or "http://localhost:11434").strip().rstrip("/")
    MODEL: str = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')
    VISION_MODEL: str = os.getenv('OLLAMA_VISION_MODEL', 'llava:7b')
    TIMEOUT: int = int(os.getenv('OLLAMA_TIMEOUT', '180'))
    # When true, collection / SSE / hybrid LLM paths refuse to run if Ollama is down or models missing
    MANDATORY: bool = os.getenv('OLLAMA_MANDATORY', 'true').strip().lower() in ('1', 'true', 'yes', 'on')
    
    @classmethod
    def is_configured(cls) -> bool:
        """Check if Ollama is configured"""
        return bool(cls.BASE)


class TelegramConfig:
    """Telegram API (MTProto user API and optional bot)"""

    API_ID: Optional[int] = None
    API_HASH: Optional[str] = None
    SESSION_NAME: str = "weapons_detection_session"
    SESSION_DIR: str = str(_BACKEND_ROOT)
    BOT_TOKEN: Optional[str] = None

    @staticmethod
    def _env_strip(value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        t = value.strip()
        if len(t) >= 2 and t[0] == t[-1] and t[0] in ('"', "'"):
            t = t[1:-1].strip()
        return t or None

    @classmethod
    def _sync_from_env(cls) -> None:
        """Reload id/hash/session paths from os.environ (handles cwd, quotes, whitespace)."""
        raw_id = cls._env_strip(os.getenv("TELEGRAM_API_ID"))
        raw_hash = cls._env_strip(os.getenv("TELEGRAM_API_HASH"))
        if not raw_id or not raw_hash:
            load_dotenv(_BACKEND_ROOT / ".env", override=True)
            load_dotenv(override=False)
            raw_id = cls._env_strip(os.getenv("TELEGRAM_API_ID"))
            raw_hash = cls._env_strip(os.getenv("TELEGRAM_API_HASH"))
        if raw_id:
            try:
                cls.API_ID = int(raw_id)
            except ValueError:
                cls.API_ID = None
        else:
            cls.API_ID = None
        cls.API_HASH = raw_hash
        cls.BOT_TOKEN = cls._env_strip(os.getenv("TELEGRAM_BOT_TOKEN"))
        sn = os.getenv("TELEGRAM_SESSION_NAME")
        cls.SESSION_NAME = cls._env_strip(sn) or "weapons_detection_session"
        sd = os.getenv("TELEGRAM_SESSION_DIR")
        cls.SESSION_DIR = cls._env_strip(sd) or str(_BACKEND_ROOT)

    @classmethod
    def session_path(cls) -> Path:
        cls._sync_from_env()
        base = Path(cls.SESSION_DIR).expanduser().resolve()
        return base / f"{cls.SESSION_NAME}.session"

    @classmethod
    def session_file_candidates(cls) -> List[Path]:
        """Where a Telethon .session file may exist (auth script cwd vs backend dir)."""
        cls._sync_from_env()
        name = f"{cls.SESSION_NAME}.session"
        roots = [
            Path(cls.SESSION_DIR).expanduser().resolve(),
            Path.cwd(),
            _BACKEND_ROOT,
            _BACKEND_ROOT / "src",
            _BACKEND_ROOT.parent,
        ]
        seen: Set[str] = set()
        out: List[Path] = []
        for r in roots:
            try:
                p = (r / name).resolve()
            except OSError:
                continue
            key = str(p)
            if key not in seen:
                seen.add(key)
                out.append(p)
        return out

    @classmethod
    def resolved_session_file(cls) -> Optional[Path]:
        for p in cls.session_file_candidates():
            if p.is_file():
                return p
        return None

    @classmethod
    def has_session_file(cls) -> bool:
        return cls.resolved_session_file() is not None

    @classmethod
    def user_api_credentials_ok(cls) -> bool:
        cls._sync_from_env()
        return cls.API_ID is not None and bool(cls.API_HASH)

    @classmethod
    def is_configured(cls) -> bool:
        """Bot token or user API id+hash present (credentials set)."""
        cls._sync_from_env()
        if cls.BOT_TOKEN:
            return True
        return cls.API_ID is not None and bool(cls.API_HASH)

    @classmethod
    def get_missing_user_api_config(cls) -> List[str]:
        cls._sync_from_env()
        missing: List[str] = []
        if cls.API_ID is None:
            missing.append('TELEGRAM_API_ID')
        if not cls.API_HASH:
            missing.append('TELEGRAM_API_HASH')
        return missing


TelegramConfig._sync_from_env()


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

    # Telegram configuration
    telegram = TelegramConfig
    
    # Ollama LLM configuration
    ollama = OllamaConfig