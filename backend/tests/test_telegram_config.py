"""Tests for Telegram session path helper."""
from pathlib import Path

import pytest

from backend_service.telegram_stream_analysis import telegram_client_session_arg
from config import TelegramConfig


def test_telegram_client_session_arg_path_without_suffix(tmp_path):
    p = tmp_path / "myapp.session"
    p.write_bytes(b"")
    arg = telegram_client_session_arg(p)
    assert arg == str(tmp_path / "myapp")


def test_telegram_client_session_arg_plain_string():
    assert telegram_client_session_arg("/tmp/foo.session") == "/tmp/foo"


def test_telegram_config_sync_from_env_strips_quotes(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("TELEGRAM_API_ID", "  12345  ")
    monkeypatch.setenv("TELEGRAM_API_HASH", '"deadbeefcafe"')
    TelegramConfig._sync_from_env()
    assert TelegramConfig.API_ID == 12345
    assert TelegramConfig.API_HASH == "deadbeefcafe"


def test_telegram_config_session_name_default_when_empty(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("TELEGRAM_SESSION_NAME", raising=False)
    TelegramConfig._sync_from_env()
    assert TelegramConfig.SESSION_NAME == "weapons_detection_session"
