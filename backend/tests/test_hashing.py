"""Tests for privacy hashing utilities."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend_service.utils.hashing import hash_username, hash_content, hash_email, hash_phone


class TestHashUsername:
    def test_anonymous_values(self):
        assert hash_username("") == "anonymous"
        assert hash_username("[deleted]") == "anonymous"
        assert hash_username("anonymous") == "anonymous"

    def test_deterministic_and_truncated(self):
        h = hash_username("alice")
        assert h == hash_username("alice")
        assert len(h) == 16

    def test_salt_changes_hash(self):
        assert hash_username("alice", salt="s1") != hash_username("alice", salt="s2")


class TestHashContent:
    def test_empty(self):
        assert hash_content("") == ""

    def test_truncated_vs_full(self):
        truncated = hash_content("hello")
        full = hash_content("hello", full_hash=True)
        assert len(truncated) == 32
        assert len(full) == 64
        assert full.startswith(truncated)


class TestHashEmail:
    def test_invalid(self):
        assert hash_email("") == "anonymous_email"
        assert hash_email("not-an-email") == "anonymous_email"

    def test_preserves_domain(self):
        result = hash_email("user@example.com")
        assert result.endswith("@example.com")
        assert not result.startswith("user@")


class TestHashPhone:
    def test_empty_or_short(self):
        assert hash_phone("") == "anonymous_phone"
        assert hash_phone("12") == "anonymous_phone"

    def test_keeps_last_four(self):
        result = hash_phone("555-123-4567")
        assert result.endswith("4567")
        assert result.startswith("***")
