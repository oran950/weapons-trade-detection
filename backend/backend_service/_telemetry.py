"""
Telemetry and logging for the backend service
"""
import logging
import sys
from typing import Optional, Dict, Any
from datetime import datetime
from functools import wraps
import time


# Configure logging
def setup_logging(level: str = "INFO", format_type: str = "standard"):
    """
    Setup logging configuration
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        format_type: 'standard' or 'json'
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    if format_type == "json":
        format_str = '{"time": "%(asctime)s", "level": "%(levelname)s", "module": "%(module)s", "message": "%(message)s"}'
    else:
        format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=log_level,
        format=format_str,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


class Logger:
    """
    Custom logger with structured logging support
    """
    
    def __init__(self, name: str = "weapons_detection"):
        self._logger = logging.getLogger(name)
    
    def _format_extra(self, extra: Optional[Dict[str, Any]] = None) -> str:
        """Format extra data for logging"""
        if not extra:
            return ""
        return " | " + " ".join(f"{k}={v}" for k, v in extra.items())
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        self._logger.debug(f"{message}{self._format_extra(extra)}")
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        self._logger.info(f"{message}{self._format_extra(extra)}")
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        self._logger.warning(f"{message}{self._format_extra(extra)}")
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None):
        self._logger.error(f"{message}{self._format_extra(extra)}")
    
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None):
        self._logger.critical(f"{message}{self._format_extra(extra)}")
    
    def analysis_complete(
        self, 
        analysis_id: str, 
        risk_score: float, 
        duration_ms: float
    ):
        """Log analysis completion"""
        self.info(
            "Analysis completed",
            extra={
                "analysis_id": analysis_id,
                "risk_score": round(risk_score, 3),
                "duration_ms": round(duration_ms, 2)
            }
        )
    
    def collection_complete(
        self,
        platform: str,
        posts_count: int,
        duration_s: float
    ):
        """Log collection completion"""
        self.info(
            "Collection completed",
            extra={
                "platform": platform,
                "posts_count": posts_count,
                "duration_s": round(duration_s, 2)
            }
        )
    
    def llm_call(
        self,
        operation: str,
        success: bool,
        latency_ms: float
    ):
        """Log LLM call"""
        level = "info" if success else "warning"
        getattr(self, level)(
            f"LLM {operation}",
            extra={
                "success": success,
                "latency_ms": round(latency_ms, 2)
            }
        )
    
    def error_occurred(self, error_type: str, message: str, details: Dict = None):
        """Log error with details"""
        self.error(
            f"{error_type}: {message}",
            extra=details
        )


def timed(logger: Logger = None):
    """
    Decorator to time function execution
    
    Usage:
        @timed(logger)
        def my_function():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start) * 1000
                if logger:
                    logger.debug(
                        f"{func.__name__} completed",
                        extra={"duration_ms": round(duration, 2)}
                    )
                return result
            except Exception as e:
                duration = (time.time() - start) * 1000
                if logger:
                    logger.error(
                        f"{func.__name__} failed",
                        extra={
                            "duration_ms": round(duration, 2),
                            "error": str(e)
                        }
                    )
                raise
        return wrapper
    return decorator


def async_timed(logger: Logger = None):
    """
    Decorator to time async function execution
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = (time.time() - start) * 1000
                if logger:
                    logger.debug(
                        f"{func.__name__} completed",
                        extra={"duration_ms": round(duration, 2)}
                    )
                return result
            except Exception as e:
                duration = (time.time() - start) * 1000
                if logger:
                    logger.error(
                        f"{func.__name__} failed",
                        extra={
                            "duration_ms": round(duration, 2),
                            "error": str(e)
                        }
                    )
                raise
        return wrapper
    return decorator


# Global logger instance
logger = Logger()

