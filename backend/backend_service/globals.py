"""
Global state management
"""
from typing import Optional, Dict, Any
from datetime import datetime


class GlobalState:
    """
    Manages global application state
    """
    
    def __init__(self):
        self._start_time: Optional[datetime] = None
        self._collections_count: int = 0
        self._analyses_count: int = 0
        self._llm_calls_count: int = 0
        self._errors_count: int = 0
        self._last_collection_time: Optional[datetime] = None
        self._last_analysis_time: Optional[datetime] = None
    
    def mark_started(self):
        """Mark application start"""
        self._start_time = datetime.now()
    
    def increment_collections(self):
        """Increment collection counter"""
        self._collections_count += 1
        self._last_collection_time = datetime.now()
    
    def increment_analyses(self):
        """Increment analysis counter"""
        self._analyses_count += 1
        self._last_analysis_time = datetime.now()
    
    def increment_llm_calls(self):
        """Increment LLM calls counter"""
        self._llm_calls_count += 1
    
    def increment_errors(self):
        """Increment error counter"""
        self._errors_count += 1
    
    @property
    def uptime_seconds(self) -> float:
        """Get uptime in seconds"""
        if not self._start_time:
            return 0.0
        return (datetime.now() - self._start_time).total_seconds()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get all statistics"""
        return {
            "start_time": self._start_time.isoformat() if self._start_time else None,
            "uptime_seconds": self.uptime_seconds,
            "collections_count": self._collections_count,
            "analyses_count": self._analyses_count,
            "llm_calls_count": self._llm_calls_count,
            "errors_count": self._errors_count,
            "last_collection": self._last_collection_time.isoformat() if self._last_collection_time else None,
            "last_analysis": self._last_analysis_time.isoformat() if self._last_analysis_time else None
        }
    
    def reset(self):
        """Reset all counters"""
        self._collections_count = 0
        self._analyses_count = 0
        self._llm_calls_count = 0
        self._errors_count = 0


# Global state instance
state = GlobalState()

