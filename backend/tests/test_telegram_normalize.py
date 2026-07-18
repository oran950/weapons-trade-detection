"""Tests for Telegram channel/source normalization."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend_service.telegram_stream_analysis import (
    normalize_telegram_channel,
    normalize_telegram_sources,
)


class TestNormalizeTelegramChannel:
    def test_strips_at(self):
        assert normalize_telegram_channel("@MyChannel") == "MyChannel"

    def test_tme_url(self):
        assert normalize_telegram_channel("https://t.me/weaponwatch") == "weaponwatch"
        assert normalize_telegram_channel("https://t.me/s/weaponwatch/12") == "weaponwatch"

    def test_joinchat_preserved(self):
        raw = "https://t.me/joinchat/AAAA"
        assert normalize_telegram_channel(raw) == raw

    def test_empty(self):
        assert normalize_telegram_channel("") == ""
        assert normalize_telegram_channel("   ") == ""


class TestNormalizeTelegramSources:
    def test_dedupes_and_normalizes(self):
        sources = normalize_telegram_sources(
            ["@alpha", "https://t.me/alpha", "beta", "beta", ""]
        )
        assert sources == ["alpha", "beta"]
