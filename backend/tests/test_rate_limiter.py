"""Tests for rate limiter utilities."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend_service.utils.rate_limiter import RateLimitConfig, RateLimiter


class TestRateLimiter:
    def test_default_config(self):
        limiter = RateLimiter()
        assert limiter.config.burst_limit == 10
        assert limiter.requests_remaining == 60

    def test_nonblocking_exhausts_burst(self):
        limiter = RateLimiter(
            RateLimitConfig(
                requests_per_second=0.01,
                requests_per_minute=100,
                burst_limit=3,
            )
        )
        assert limiter.acquire(blocking=False) is True
        assert limiter.acquire(blocking=False) is True
        assert limiter.acquire(blocking=False) is True
        assert limiter.acquire(blocking=False) is False

    def test_reset_restores_tokens(self):
        limiter = RateLimiter(RateLimitConfig(burst_limit=2, requests_per_minute=100))
        limiter.acquire(blocking=False)
        limiter.acquire(blocking=False)
        assert limiter.acquire(blocking=False) is False
        limiter.reset()
        assert limiter.acquire(blocking=False) is True

    def test_requests_remaining_decreases(self):
        limiter = RateLimiter(RateLimitConfig(burst_limit=5, requests_per_minute=5))
        before = limiter.requests_remaining
        limiter.acquire(blocking=False)
        assert limiter.requests_remaining == before - 1
