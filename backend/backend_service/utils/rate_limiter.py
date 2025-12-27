"""
Rate limiting utilities for API calls
"""
import time
import asyncio
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import threading


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""
    requests_per_second: float = 1.0
    requests_per_minute: int = 60
    burst_limit: int = 10
    retry_after_seconds: int = 60


class RateLimiter:
    """
    Thread-safe rate limiter for API calls
    
    Implements token bucket algorithm with both per-second
    and per-minute limits.
    """
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        self._lock = threading.Lock()
        self._last_request_time = 0.0
        self._minute_requests: deque = deque()
        self._tokens = float(self.config.burst_limit)
        self._last_token_update = time.time()
    
    def _update_tokens(self) -> None:
        """Update token count based on elapsed time"""
        now = time.time()
        elapsed = now - self._last_token_update
        self._tokens = min(
            self.config.burst_limit,
            self._tokens + elapsed * self.config.requests_per_second
        )
        self._last_token_update = now
    
    def _clean_minute_window(self) -> None:
        """Remove requests older than 1 minute"""
        cutoff = time.time() - 60
        while self._minute_requests and self._minute_requests[0] < cutoff:
            self._minute_requests.popleft()
    
    def acquire(self, blocking: bool = True) -> bool:
        """
        Acquire permission to make a request
        
        Args:
            blocking: If True, wait until rate limit allows request
            
        Returns:
            True if request is allowed, False otherwise
        """
        with self._lock:
            self._update_tokens()
            self._clean_minute_window()
            
            # Check per-minute limit
            if len(self._minute_requests) >= self.config.requests_per_minute:
                if blocking:
                    wait_time = 60 - (time.time() - self._minute_requests[0])
                    if wait_time > 0:
                        time.sleep(wait_time)
                    self._clean_minute_window()
                else:
                    return False
            
            # Check token bucket
            if self._tokens < 1:
                if blocking:
                    wait_time = (1 - self._tokens) / self.config.requests_per_second
                    time.sleep(wait_time)
                    self._update_tokens()
                else:
                    return False
            
            # Consume token and record request
            self._tokens -= 1
            self._minute_requests.append(time.time())
            self._last_request_time = time.time()
            return True
    
    async def acquire_async(self, blocking: bool = True) -> bool:
        """
        Async version of acquire
        """
        with self._lock:
            self._update_tokens()
            self._clean_minute_window()
            
            if len(self._minute_requests) >= self.config.requests_per_minute:
                if blocking:
                    wait_time = 60 - (time.time() - self._minute_requests[0])
                    if wait_time > 0:
                        await asyncio.sleep(wait_time)
                    self._clean_minute_window()
                else:
                    return False
            
            if self._tokens < 1:
                if blocking:
                    wait_time = (1 - self._tokens) / self.config.requests_per_second
                    await asyncio.sleep(wait_time)
                    self._update_tokens()
                else:
                    return False
            
            self._tokens -= 1
            self._minute_requests.append(time.time())
            return True
    
    def wait(self, seconds: float) -> None:
        """
        Wait for specified seconds (respects rate limiting)
        """
        time.sleep(seconds)
    
    async def wait_async(self, seconds: float) -> None:
        """
        Async wait for specified seconds
        """
        await asyncio.sleep(seconds)
    
    @property
    def requests_remaining(self) -> int:
        """Get number of requests remaining in current minute window"""
        self._clean_minute_window()
        return max(0, self.config.requests_per_minute - len(self._minute_requests))
    
    def reset(self) -> None:
        """Reset rate limiter state"""
        with self._lock:
            self._minute_requests.clear()
            self._tokens = float(self.config.burst_limit)
            self._last_token_update = time.time()

