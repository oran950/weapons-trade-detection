"""Tests for configuration helpers beyond Telegram session basics."""
import sys
import os
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import RedditConfig, OllamaConfig, TelegramConfig, AppConfig


class TestRedditConfig:
    def test_is_configured_when_complete(self):
        RedditConfig.CLIENT_ID = "id"
        RedditConfig.CLIENT_SECRET = "secret"
        RedditConfig.USER_AGENT = "agent"
        assert RedditConfig.is_configured() is True
        assert RedditConfig.get_missing_config() == []

    def test_missing_items(self):
        RedditConfig.CLIENT_ID = None
        RedditConfig.CLIENT_SECRET = "secret"
        RedditConfig.USER_AGENT = None
        assert RedditConfig.is_configured() is False
        missing = RedditConfig.get_missing_config()
        assert "REDDIT_CLIENT_ID" in missing
        assert "REDDIT_USER_AGENT" in missing


class TestOllamaConfig:
    def test_is_configured_with_base(self):
        OllamaConfig.BASE = "http://localhost:11434"
        assert OllamaConfig.is_configured() is True

    def test_mandatory_parsing(self, monkeypatch):
        monkeypatch.setenv("OLLAMA_MANDATORY", "yes")
        assert os.getenv("OLLAMA_MANDATORY", "").strip().lower() in ("1", "true", "yes", "on")
        monkeypatch.setenv("OLLAMA_MANDATORY", "false")
        assert os.getenv("OLLAMA_MANDATORY", "").strip().lower() not in ("1", "true", "yes", "on")


class TestTelegramConfigExtended:
    def test_env_strip(self):
        assert TelegramConfig._env_strip(None) is None
        assert TelegramConfig._env_strip("  abc  ") == "abc"
        assert TelegramConfig._env_strip('"quoted"') == "quoted"
        assert TelegramConfig._env_strip("'quoted'") == "quoted"
        assert TelegramConfig._env_strip("   ") is None

    def test_invalid_api_id(self, monkeypatch):
        monkeypatch.setenv("TELEGRAM_API_ID", "not-a-number")
        monkeypatch.setenv("TELEGRAM_API_HASH", "deadbeef")
        TelegramConfig._sync_from_env()
        assert TelegramConfig.API_ID is None
        assert TelegramConfig.API_HASH == "deadbeef"

    def test_session_path(self, monkeypatch, tmp_path):
        monkeypatch.setenv("TELEGRAM_SESSION_DIR", str(tmp_path))
        monkeypatch.setenv("TELEGRAM_SESSION_NAME", "research")
        path = TelegramConfig.session_path()
        assert path == (tmp_path / "research.session").resolve()

    def test_resolved_session_file(self, monkeypatch, tmp_path):
        monkeypatch.setenv("TELEGRAM_SESSION_DIR", str(tmp_path))
        monkeypatch.setenv("TELEGRAM_SESSION_NAME", "sess")
        TelegramConfig._sync_from_env()
        assert TelegramConfig.has_session_file() is False
        session = tmp_path / "sess.session"
        session.write_bytes(b"x")
        assert TelegramConfig.resolved_session_file() == session.resolve()
        assert TelegramConfig.has_session_file() is True

    def test_bot_token_configures(self, monkeypatch):
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:ABC")
        monkeypatch.delenv("TELEGRAM_API_ID", raising=False)
        monkeypatch.delenv("TELEGRAM_API_HASH", raising=False)
        TelegramConfig.API_ID = None
        TelegramConfig.API_HASH = None
        TelegramConfig._sync_from_env()
        assert TelegramConfig.is_configured() is True

    def test_missing_user_api_config(self, monkeypatch):
        # Prevent .env reload from filling placeholder credentials
        monkeypatch.setenv("TELEGRAM_API_ID", "")
        monkeypatch.setenv("TELEGRAM_API_HASH", "")
        monkeypatch.setattr("config.load_dotenv", lambda *args, **kwargs: False)
        TelegramConfig._sync_from_env()
        missing = TelegramConfig.get_missing_user_api_config()
        assert "TELEGRAM_API_ID" in missing
        assert "TELEGRAM_API_HASH" in missing


class TestAppConfig:
    def test_defaults_present(self):
        assert AppConfig.HOST
        assert AppConfig.PORT == 9000 or isinstance(AppConfig.PORT, int)
        assert AppConfig.reddit is RedditConfig
        assert AppConfig.telegram is TelegramConfig
        assert AppConfig.ollama is OllamaConfig
